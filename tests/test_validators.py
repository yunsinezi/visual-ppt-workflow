import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillValidationTest(unittest.TestCase):
    def test_skill(self):
        self.assertEqual(load('validate_skill').validate(ROOT), [])

    def test_project_template(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_image_branch_template_has_no_a_gates(self):
        manifest = json.loads((ROOT / 'assets/image-branch-template.json').read_text(encoding='utf8'))
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_missing_route_selection_is_flagged(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['gates']['branch_selected'] = False
        self.assertTrue(any('A/B selection' in x for x in load('validate_project').validate(manifest)))

    def test_image_branch_cannot_enter_a_stages(self):
        manifest = json.loads((ROOT / 'assets/image-branch-template.json').read_text(encoding='utf8'))
        manifest['stage'] = 'build'
        self.assertTrue(any('B cannot enter A' in x for x in load('validate_project').validate(manifest)))

    def b_manifest(self):
        return json.loads((ROOT / 'assets/image-branch-template.json').read_text(encoding='utf8'))

    def preview_ready(self, manifest):
        manifest['stage'] = 'b_await_confirmation'
        manifest['b_previews'] = {
            'slide_id': manifest['slides'][0]['id'],
            'B1': 'previews/B1.png',
            'B2': 'previews/B2.png'
        }
        manifest['gates']['b_previews_generated'] = True
        manifest['b_previews']['prompt_base'] = '同一页：代表性内容'
        manifest['b_previews']['prompt_B1'] = '同一页：代表性内容'
        manifest['b_previews']['prompt_B2'] = '同一页：代表性内容' + '\n' + load('validate_project').B2_QUALITY_CONSTRAINT
        return manifest

    def confirmed(self, manifest, mode='both'):
        manifest = self.preview_ready(manifest)
        manifest['stage'] = 'image_generate'
        manifest['b_generation_mode'] = mode
        manifest['gates']['b_variant_confirmed'] = True
        return manifest

    def test_preview_gate_is_valid_only_after_pair(self):
        manifest = self.b_manifest()
        manifest['stage'] = 'b_await_confirmation'
        self.assertTrue(load('validate_project').validate(manifest))
        self.assertEqual(load('validate_project').validate(self.preview_ready(manifest)), [])

    def test_preview_must_use_two_distinct_files(self):
        manifest = self.preview_ready(self.b_manifest())
        manifest['b_previews']['B2'] = manifest['b_previews']['B1']
        self.assertTrue(any('distinct' in err for err in load('validate_project').validate(manifest)))

    def test_b_cannot_batch_without_user_choice(self):
        manifest = self.preview_ready(self.b_manifest())
        manifest['stage'] = 'image_generate'
        self.assertTrue(any('user confirmation' in err for err in load('validate_project').validate(manifest)))

    def test_default_both_requires_explicit_confirmation(self):
        manifest = self.preview_ready(self.b_manifest())
        manifest['b_generation_mode'] = 'both'
        self.assertTrue(any('wait for user confirmation' in err for err in load('validate_project').validate(manifest)))
        self.assertEqual(load('validate_project').validate(self.confirmed(self.b_manifest())), [])

    def add_variant_deliveries(self, manifest, mode='both'):
        variants = ('B1', 'B2') if mode == 'both' else (mode,)
        for variant in variants:
            manifest['artifacts']['variant_deliveries'][variant] = {
                'images_dir': f'{variant}/',
                'images_zip': f'{variant}/images.zip',
                'pptx': f'{variant}/deck-image-only.pptx',
            }
        return manifest

    def test_image_branch_delivered_requires_both_decks_and_qa(self):
        manifest = self.confirmed(self.b_manifest())
        manifest['stage'] = 'image_delivered'
        self.assertTrue(load('validate_project').validate(manifest))
        for slide in manifest['slides']:
            slide['prompt_base'] = f"完整页内容及比例: {slide['id']}"
            for variant in ('B1', 'B2'):
                slide['variant_images'][variant] = f"{variant}/{slide['id']}.png"
                slide['variant_qa'][variant] = 'pass'
                slide['variant_prompts'][variant] = slide['prompt_base'] + ('\n' + load('validate_project').B2_QUALITY_CONSTRAINT if variant == 'B2' else '')
        self.add_variant_deliveries(manifest)
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_one_branch_only_needs_its_own_deck(self):
        manifest = self.confirmed(self.b_manifest(), 'B1')
        manifest['stage'] = 'image_delivered'
        for slide in manifest['slides']:
            slide['prompt_base'] = f"Page: {slide['id']}"
            slide['variant_images']['B1'] = f"B1/{slide['id']}.png"
            slide['variant_qa']['B1'] = 'pass'
            slide['variant_prompts']['B1'] = slide['prompt_base']
        self.add_variant_deliveries(manifest, 'B1')
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_b2_constraint_has_to_be_exact(self):
        manifest = self.confirmed(self.b_manifest(), 'B2')
        manifest['stage'] = 'image_delivered'
        for slide in manifest['slides']:
            slide['prompt_base'] = f"Page: {slide['id']}"
            slide['variant_images']['B2'] = f"B2/{slide['id']}.png"
            slide['variant_qa']['B2'] = 'pass'
            slide['variant_prompts']['B2'] = slide['prompt_base'] + '\n' + 'over-sharpened HDR'
        self.assertTrue(any('prompt policy mismatch' in e for e in load('validate_project').validate(manifest)))

    def test_legacy_v21_b_manifest_is_accepted(self):
        manifest = self.b_manifest()
        manifest['schema_version'] = '1.1'
        manifest['stage'] = 'image_generate'
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_a_without_animation_but_editable_is_valid(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['brief']['animation_requested'] = False
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_a_requires_animation_or_editability(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['brief']['animation_requested'] = False
        manifest['brief']['editable_requested'] = False
        self.assertTrue(any('animation OR element-level' in x for x in load('validate_project').validate(manifest)))

    def test_b_editability_requirement_mismatch(self):
        manifest = self.b_manifest()
        manifest['brief']['editable_requested'] = True
        self.assertTrue(any('editable_requested=false' in x for x in load('validate_project').validate(manifest)))

    def test_b_preview_prompt_pair_must_share_base(self):
        manifest = self.preview_ready(self.b_manifest())
        manifest['b_previews']['prompt_B2'] = '强制摄影，改变画风'
        self.assertTrue(any('preview prompt policy' in x for x in load('validate_project').validate(manifest)))

    def test_b_delivery_requires_zip_and_flattened_pptx(self):
        manifest = self.confirmed(self.b_manifest(), 'B1')
        manifest['stage'] = 'image_delivered'
        for slide in manifest['slides']:
            slide['prompt_base'] = f'Page: {slide["id"]}'
            slide['variant_images']['B1'] = f'B1/{slide["id"]}.png'
            slide['variant_qa']['B1'] = 'pass'
            slide['variant_prompts']['B1'] = slide['prompt_base']
        self.add_variant_deliveries(manifest, 'B1')
        manifest['artifacts']['variant_deliveries']['B1']['images_zip'] = None
        self.assertTrue(any('images_zip' in x for x in load('validate_project').validate(manifest)))

    def test_important_a_outline_gate_and_16_styleboards(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['brief']['complexity'] = 'important'
        manifest['stage'] = 'styles'
        self.assertTrue(any('outline_approved' in x for x in load('validate_project').validate(manifest)))
        manifest['gates']['outline_approved'] = True
        manifest['stage'] = 'selected'
        manifest['gates']['style_selected'] = True
        manifest['selected_style_id'] = 'style-01'
        manifest['styleboards'] = [f'style-{i:02d}.png' for i in range(8)]
        self.assertTrue(any('16 styleboard' in x for x in load('validate_project').validate(manifest)))
        manifest['styleboards'] = [f'style-{i:02d}.png' for i in range(16)]
        self.assertEqual(load('validate_project').validate(manifest), [])

    def test_b_delivered_requires_real_png_paths(self):
        manifest = self.confirmed(self.b_manifest(), 'B1')
        manifest['stage'] = 'image_delivered'
        for slide in manifest['slides']:
            slide['prompt_base'] = f'Page: {slide["id"]}'
            slide['variant_images']['B1'] = f'B1/{slide["id"]}.jpg'
            slide['variant_qa']['B1'] = 'pass'
            slide['variant_prompts']['B1'] = slide['prompt_base']
        self.add_variant_deliveries(manifest, 'B1')
        self.assertTrue(any('must be PNG' in x for x in load('validate_project').validate(manifest)))

    def test_a_delivery_requires_pdf_and_overview(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['stage'] = 'delivered'
        manifest['gates']['style_selected'] = True
        manifest['gates']['artwork_approved'] = True
        manifest['selected_style_id'] = 'style-01'
        manifest['styleboards'] = ['style-' + str(i) for i in range(8)]
        for slide in manifest['slides']:
            slide['reference_image'] = slide['id'] + '.png'
        self.assertTrue(any('overview_image' in x for x in load('validate_project').validate(manifest)))

    def test_b_animation_requirement_mismatch(self):
        manifest = json.loads((ROOT / 'assets/image-branch-template.json').read_text(encoding='utf8'))
        manifest['brief']['animation_requested'] = True
        self.assertTrue(any('animation_requested' in x for x in load('validate_project').validate(manifest)))

    def test_fake_approval_is_flagged(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['stage'] = 'approved'
        self.assertTrue(load('validate_project').validate(manifest))

    def test_faux_editability_is_flagged(self):
        manifest = json.loads((ROOT / 'assets/project-template.json').read_text(encoding='utf8'))
        manifest['slides'][0]['elements'][0]['kind'] = 'flattened_page'
        self.assertTrue(any('flattened_page' in x for x in load('validate_project').validate(manifest)))


if __name__ == '__main__':
    unittest.main()
