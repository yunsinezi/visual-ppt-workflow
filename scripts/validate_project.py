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
