#!/usr/bin/env python3
"""Static self-consistency validator for visual-ppt-workflow project.json.

Gate markers are user/agent claims; this script cannot prove approval or visual quality.
"""
import argparse
import json
import sys
from pathlib import Path

STAGES_A = ('brief', 'styles', 'selected', 'pilot', 'artwork', 'approved', 'build', 'qa', 'delivered')
STAGES_B = ('b_preview', 'b_await_confirmation', 'image_generate', 'image_qa', 'image_delivered')
B_OPTIONS = ('B1', 'B2', 'both')
B2_QUALITY_CONSTRAINT = "画面保持干净自然的真实照片质感：不要数字噪点与彩色噪点，不要颗粒覆盖，不要过度锐化，不要 HDR 与油腻高光，不要蜡质表面，不要脏灰色调，不要假细节与压缩伪影。"
STAGES = ('route',) + STAGES_A + STAGES_B
MODES = ('editable', 'image', 'hybrid', 'review', 'pdf-only')
KINDS = ('background', 'native_text', 'native_shape', 'native_chart', 'native_table', 'independent_image', 'flattened_page')
QA_VALUES = ('not_tested', 'pass', 'fail', 'not_applicable', 'blocked')


def validate(project):
    if project.get('schema_version') == '2.0':
        return validate_style_first(project)
    errors = []
    for name in ('schema_version', 'project_id', 'workflow_branch', 'mode', 'stage', 'brief', 'gates', 'slides', 'artifacts'):
        if name not in project:
            errors.append(f'missing field: {name}')
    if errors:
        return errors
    if project['mode'] not in MODES:
        errors.append('unsupported mode')
    stage = project['stage']
    if stage not in STAGES:
        errors.append('unsupported stage')
    slides = project['slides']
    if not isinstance(slides, list) or not slides:
        errors.append('slides must be a nonempty array')
        return errors
    gates = project['gates']
    branch = project['workflow_branch']
    if branch not in ('A', 'B', None):
        errors.append('workflow_branch must be A or B (or null only at route stage)')
    if stage == 'route':
        if gates.get('branch_selected'):
            errors.append('route stage cannot claim branch_selected')
    elif branch not in ('A', 'B') or not gates.get('branch_selected'):
        errors.append('generation stages require explicit A/B selection and gates.branch_selected')
    if branch == 'A':
        if stage in STAGES_B:
            errors.append('A cannot enter image-only stages')
        wants_animation = project['brief'].get('animation_requested')
        wants_edit = project['brief'].get('editable_requested')
        if not isinstance(wants_animation, bool):
            errors.append('A requires boolean brief.animation_requested')
        if project.get('schema_version') == '1.2' and not isinstance(wants_edit, bool):
            errors.append('A schema 1.2 requires boolean brief.editable_requested')
        # A is correct for animation OR element-level editability; it can have no animation.
        if wants_animation is False and wants_edit is not True:
            errors.append('A requires animation OR element-level editability')
        if project.get('schema_version') == '1.2':
            complexity = project['brief'].get('complexity')
            if complexity not in ('ordinary', 'important'):
                errors.append('A v1.2 brief.complexity must be ordinary or important')
            if complexity == 'important' and stage in STAGES_A[1:] and not gates.get('outline_approved'):
                errors.append('important A requires outline_approved before visual exploration')
        if stage in STAGES_A[2:] and not gates.get('style_selected') and project['mode'] not in ('review',):
            errors.append('A selected+ stage requires gates.style_selected, unless review')
        if stage in STAGES_A[5:] and not gates.get('artwork_approved') and project['mode'] not in ('review',):
            errors.append('A approved+ stage requires gates.artwork_approved, unless review')
        if gates.get('style_selected') and not project.get('selected_style_id'):
            errors.append('selected style gate requires selected_style_id')
        expected_previews = 16 if project.get('schema_version') == '1.2' and project['brief'].get('complexity') == 'important' else 8
        waiver = bool(project.get('preview_waiver')) if project.get('schema_version') != '1.2' else False
        if gates.get('style_selected') and len(project.get('styleboards', [])) < expected_previews and not waiver:
            errors.append(f'style_selected requires {expected_previews} styleboard images')
        if stage in STAGES_A[5:] and not all(s.get('reference_image') for s in slides) and project['mode'] not in ('review',):
            errors.append('A approved+ stage requires reference_image for every slide')
    if branch == 'B':
        if stage not in STAGES_B and stage != 'route':
            errors.append('B cannot enter A workflow stages')
        if project['mode'] != 'image':
            errors.append('B requires mode=image')
        if project['brief'].get('animation_requested') is not False:
            errors.append('B must have animation_requested=false')
        if project.get('schema_version') == '1.3' and project['brief'].get('editable_requested') is not False:
            errors.append('B schema 1.3 requires editable_requested=false')
        if gates.get('style_selected') or gates.get('artwork_approved'):
            errors.append('B must not claim A-only style/artwork gates')
        # Preserve validation of work already started under v2.1; do not retroactively
        # demand a preview gate for old projects that are being resumed.
        if project.get('schema_version') == '1.1':
            if stage == 'image_delivered':
                for item in slides:
                    if not item.get('rendered_image'):
                        errors.append(f'legacy B image_delivered requires rendered_image for {item.get("id")}')
                    if item.get('qa', {}).get('static') != 'pass':
                        errors.append(f'legacy B image_delivered requires static QA pass for {item.get("id")}')
        else:
            if project.get('schema_version') not in ('1.2', '1.3'):
                errors.append('B workflow requires schema_version 1.3 (or older 1.1/1.2 legacy)')
            previews = project.get('b_previews')
            if not isinstance(previews, dict):
                errors.append('B requires b_previews object')
                previews = {}
            mode = project.get('b_generation_mode')
            if mode not in (*B_OPTIONS, None):
                errors.append('B b_generation_mode must be B1, B2, both, or null')
            if stage in ('b_await_confirmation', 'image_generate', 'image_qa', 'image_delivered'):
                if not gates.get('b_previews_generated'):
                    errors.append('B requires both preview images before confirmation or generation')
                if not all(isinstance(previews.get(k), str) and previews.get(k) for k in ('slide_id','B1','B2')):
                    errors.append('B paired previews require the same slide_id and separate B1/B2 image paths')
                if previews.get('B1') and previews.get('B1') == previews.get('B2'):
                    errors.append('B paired previews must be distinct image paths')
                if project.get('schema_version') == '1.3':
                    base_prompt = previews.get('prompt_base')
                    if not isinstance(base_prompt, str) or not base_prompt:
                        errors.append('B v1.3 paired preview requires shared prompt_base')
                    elif (previews.get('prompt_B1') != base_prompt or
                          previews.get('prompt_B2') != base_prompt + '\n' + B2_QUALITY_CONSTRAINT):
                        errors.append('B paired preview prompt policy mismatch')
            if stage in ('route', 'b_preview', 'b_await_confirmation'):
                if gates.get('b_variant_confirmed') or mode is not None:
                    errors.append('B must wait for user confirmation after paired preview before choosing a variant')
            if stage in ('image_generate', 'image_qa', 'image_delivered'):
                if not gates.get('b_variant_confirmed') or mode not in B_OPTIONS:
                    errors.append('B cannot batch generate before explicit B1/B2/both user confirmation')
            if stage == 'image_delivered' and mode in B_OPTIONS:
                variants = ('B1','B2') if mode == 'both' else (mode,)
                if project.get('schema_version') == '1.3':
                    manifest = project.get('artifacts') or {}
                    variant_deliveries = manifest.get('variant_deliveries') or {}
                    for variant in variants:
                        delivery = variant_deliveries.get(variant) or {}
                        for key in ('images_dir', 'images_zip', 'pptx'):
                            value = delivery.get(key)
                            if not isinstance(value, str) or not value:
                                errors.append(f'B image_delivered requires {variant} {key} in variant_deliveries')
                            elif not value.replace('\\\\', '/').startswith(variant + '/'):
                                errors.append(f'B {variant} {key} must be stored under {variant}/')
                for slide in slides:
                    sid = slide.get('id')
                    base = slide.get('prompt_base')
                    paths = slide.get('variant_images') or {}
                    checks = slide.get('variant_qa') or {}
                    prompts = slide.get('variant_prompts') or {}
                    for variant in variants:
                        path = paths.get(variant)
                        if not isinstance(path,str) or not path:
                            errors.append(f'B image_delivered requires {variant} image for {sid}')
                        elif not path.replace('\\\\','/').startswith(variant+'/'):
                            errors.append(f'B {variant} image for {sid} must be stored under {variant}/')
                        if checks.get(variant) != 'pass':
                            errors.append(f'B image_delivered requires {variant} QA pass for {sid}')
                        if project.get('schema_version') == '1.3' and isinstance(path, str) and not path.lower().endswith('.png'):
                            errors.append(f'B {variant} image for {sid} must be PNG')
                        if not isinstance(base, str) or not base:
                            errors.append(f'B image_delivered requires prompt_base for {sid}')
                        elif prompts.get(variant) != base + (('\n' + B2_QUALITY_CONSTRAINT) if variant == 'B2' else ''):
                            errors.append(f'B {variant} prompt policy mismatch for {sid}')
    if project.get('schema_version') in ('1.2', '1.3') and stage in ('delivered', 'image_delivered'):
        if not isinstance(project.get('build_id'), str) or not project['build_id']:
            errors.append('delivered manifest requires nonempty build_id')
        checkpoint = project.get('checkpoint') or {}
        if not isinstance(checkpoint.get('verified_files'), list):
            errors.append('delivered manifest requires checkpoint.verified_files list')
    if branch == 'A' and project.get('schema_version') == '1.2' and stage == 'delivered':
        artifacts = project.get('artifacts') or {}
        for key in ('pptx', 'pdf', 'preview_dir', 'overview_image'):
            if not artifacts.get(key):
                errors.append(f'A delivered requires artifacts.{key}')
        for slide in slides:
            qa = slide.get('qa') or {}
            if qa.get('static') != 'pass' or qa.get('edit') != 'pass':
                errors.append(f'A delivered requires static/edit QA pass for {slide.get("id")}')
            if project['brief'].get('animation_requested') is True:
                if qa.get('animation') != 'pass' and not gates.get('animation_downgrade_approved'):
                    errors.append(f'A delivered requires implemented animation or approved downgrade for {slide.get("id")}')
                if qa.get('target_playback') not in ('pass',) and not gates.get('unverified_critical_approved'):
                    errors.append(f'A delivered unverified playback requires explicit approval for {slide.get("id")}')
    ids = set()
    for idx, slide in enumerate(slides, 1):
        name = f'slides[{idx}]'
        sid = slide.get('id')
        if not sid:
            errors.append(f'{name} id required')
        elif sid in ids:
            errors.append(f'duplicate slide id {sid}')
        ids.add(sid)
        eids = set()
        for element in slide.get('elements', []):
            eid = element.get('id')
            if not eid or eid in eids:
                errors.append(f'{name} element has missing/duplicate id')
            eids.add(eid)
            kind = element.get('kind')
            if kind not in KINDS:
                errors.append(f'{name}: invalid element kind {kind}')
            bbox = element.get('bbox')
            if not (isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(v, (int, float)) for v in bbox) and bbox[2] > 0 and bbox[3] > 0):
                errors.append(f'{name} element {eid}: bbox must be [x,y,w,h], positive size')
            if branch == 'B' and (kind != 'flattened_page' or element.get('editable') is True):
                errors.append(f'{name} element {eid}: B only permits non-editable flattened_page')
            if kind == 'flattened_page' and project['mode'] == 'editable':
                errors.append(f'{name} element {eid}: flattened_page prohibited in editable mode without mode change')
        for dim, value in slide.get('qa', {}).items():
            if value not in QA_VALUES:
                errors.append(f'{name} qa.{dim} unknown: {value}')
        if stage in ('delivered', 'image_delivered') and any(x == 'fail' for x in slide.get('qa', {}).values()):
            errors.append(f'{name}: stage delivered but QA contains fail')
    return errors



def validate_style_first(project):
    """Check v2.4 STYLE-FIRST project manifest declarations.

    Paths and gate booleans cannot prove real images were generated or shown.
    """
    errors = []
    required = ('project_id', 'build_id', 'brief', 'stage', 'workflow_branch',
                'gates', 'style_previews', 'styleboards', 'selected_style_id',
                'slides', 'artifacts', 'checkpoint')
    for key in required:
        if key not in project:
            errors.append(f'missing field: {key}')
    if errors:
        return errors
    stages = ('brief', 'style_generate', 'style_await_selection', 'route',
              'pilot', 'artwork', 'approved', 'build', 'qa', 'delivered',
              'b_preview', 'b_await_confirmation', 'image_generate',
              'image_qa', 'image_delivered')
    stage = project['stage']
    if stage not in stages:
        return ['invalid STYLE-FIRST stage']
    gates = project['gates']
    branch = project['workflow_branch']
    previews = project['style_previews']
    styleboards = project['styleboards']
    brief = project['brief']
    slides = project['slides']
    if not isinstance(slides, list) or not slides:
        errors.append('slides must be a nonempty list')
    if not isinstance(previews, dict):
        errors.append('style_previews must be an object')
        previews = {}
    if not isinstance(styleboards, list):
        errors.append('styleboards must be a list')
        styleboards = []
    if not isinstance(gates, dict):
        return errors + ['gates must be an object']
    before_route = ('brief', 'style_generate', 'style_await_selection', 'route')
    after_generate = ('style_await_selection', 'route')
    expected_styles = [f'styleboards/style-{n:02d}.png' for n in range(1, 9)]
    if stage in after_generate or stage not in before_route:
        if styleboards != expected_styles:
            errors.append('eight distinct ordered styleboard PNGs required')
        if not all(previews.get(k) for k in ('slide_id', 'shared_copy', 'aspect_ratio')):
            errors.append('style previews require one shared representative slide')
        if previews.get('images') != expected_styles:
            errors.append('style preview paths must match eight styleboards')
        if gates.get('style_previews_generated') is not True:
            errors.append('eight style images must be generated before route')
        if previews.get('displayed') is not True:
            errors.append('eight style previews must be displayed before route')
    if stage in ('brief', 'style_generate', 'style_await_selection'):
        if branch is not None or gates.get('branch_selected'):
            errors.append('A/B branching prohibited until style has been chosen')
        if gates.get('style_selected') or project.get('selected_style_id'):
            errors.append('style must not be selected before user chooses from eight images')
    elif stage == 'route':
        if branch is not None or gates.get('branch_selected'):
            errors.append('route cannot branch before selected style is recorded')
    else:
        if branch not in ('A', 'B') or gates.get('branch_selected') is not True:
            errors.append('A/B branching requires user decision after style selection')
    if stage == 'route' or stage not in before_route:
        selected = project.get('selected_style_id')
        if selected not in [f'style-{n:02d}' for n in range(1, 9)] or gates.get('style_selected') is not True:
            errors.append('selected_style_id and gate required after eight previews')
    if stage in ('pilot', 'artwork', 'approved', 'build', 'qa', 'delivered'):
        if branch != 'A':
            errors.append('A stage requires workflow_branch A')
        if brief.get('animation_requested') is not True and brief.get('editable_requested') is not True:
            errors.append('A requires animation OR editability')
        if stage in ('approved','build','qa','delivered') and not gates.get('artwork_approved'):
            errors.append('A requires full artwork approval before build')
        if stage == 'delivered':
            art = project['artifacts']
            for key in ('pptx','pdf','preview_dir','overview_image'):
                if not art.get(key):
                    errors.append(f'A delivered requires {key}')
            for slide in slides:
                qa = slide.get('qa', {})
                if qa.get('static') != 'pass' or qa.get('edit') != 'pass':
                    errors.append('A delivery requires static/edit QA pass')
                if brief.get('animation_requested') is True and qa.get('animation') != 'pass' and not gates.get('animation_downgrade_approved'):
                    errors.append('A requested animation requires implementation or approved downgrade')
    b_stages = ('b_preview', 'b_await_confirmation','image_generate','image_qa','image_delivered')
    if stage in b_stages:
        if branch != 'B':
            errors.append('B stage requires workflow_branch B')
        if brief.get('animation_requested') is not False or brief.get('editable_requested') is not False:
            errors.append('B requires both animation_requested and editable_requested false')
        if stage in b_stages[1:]:
            pair = project.get('b_previews') or {}
            if not all(pair.get(k) for k in ('slide_id','B1','B2','prompt_base')):
                errors.append('B requires two same-style, same-page quality previews')
            if pair.get('B1') and pair.get('B1') == pair.get('B2'):
                errors.append('B1 and B2 preview images must be distinct')
            base_prompt = pair.get('prompt_base')
            if isinstance(base_prompt, str):
                if pair.get('prompt_B1') != base_prompt or pair.get('prompt_B2') != base_prompt + '\n' + B2_QUALITY_CONSTRAINT:
                    errors.append('B1/B2 quality prompts must share base and only differ by exact B2 suffix')
            if not gates.get('b_previews_generated'):
                errors.append('B preview pair required before variant confirmation')
        chosen = project.get('b_generation_mode')
        if stage in ('b_preview','b_await_confirmation'):
            if chosen is not None or gates.get('b_variant_confirmed'):
                errors.append('B cannot select variant before paired previews')
        else:
            if chosen not in ('B1','B2','both') or not gates.get('b_variant_confirmed'):
                errors.append('B requires confirmation of B1, B2 or both')
            if stage == 'image_delivered' and chosen in ('B1','B2','both'):
                variants = ('B1','B2') if chosen == 'both' else (chosen,)
                deliveries = (project['artifacts'].get('variant_deliveries') or {})
                for variant in variants:
                    delivery = deliveries.get(variant) or {}
                    for key in ('images_dir','images_zip','pptx'):
                        val = delivery.get(key)
                        if not isinstance(val,str) or not val.startswith(variant+'/'):
                            errors.append(f'B delivered requires {variant}/{key} path')
                for slide in slides:
                    base_prompt = slide.get('prompt_base')
                    imgs = slide.get('variant_images') or {}
                    prompts = slide.get('variant_prompts') or {}
                    checks = slide.get('variant_qa') or {}
                    for variant in variants:
                        image = imgs.get(variant)
                        if not isinstance(image,str) or not image.startswith(variant+'/') or not image.endswith('.png'):
                            errors.append(f'B {variant} missing PNG page')
                        if checks.get(variant) != 'pass':
                            errors.append(f'B {variant} missing QA pass')
                        if not isinstance(base_prompt,str) or prompts.get(variant) != base_prompt + ('\n'+B2_QUALITY_CONSTRAINT if variant == 'B2' else ''):
                            errors.append(f'B {variant} prompt policy mismatch')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', help='path to project.json')
    args = p.parse_args()
    try:
        project = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    errors = validate(project)
    if errors:
        for issue in errors:
            print('FAIL:', issue, file=sys.stderr)
        return 1
    print(f'PASS: project manifest with {len(project["slides"])} slides, stage={project["stage"]}, mode={project["mode"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
