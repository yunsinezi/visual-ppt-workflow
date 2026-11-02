import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('vpw_validator_v24',ROOT/'scripts'/'validate_project.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def sample(stage='style_generate'):
    data=json.loads((ROOT/'assets'/'style-first-template.json').read_text(encoding='utf8'))
    data['stage']=stage
    return data

def with_style(data):
    images=[f'styleboards/style-{n:02d}.png' for n in range(1,9)]
    data['styleboards']=images
    data['style_previews']['images']=images
    data['style_previews']['displayed']=True
    data['gates']['style_previews_generated']=True
    return data

def selected(data,style='style-03'):
    with_style(data)
    data['selected_style_id']=style
    data['gates']['style_selected']=True
    return data

def branch(data,which):
    selected(data)
    data['workflow_branch']=which
    data['gates']['branch_selected']=True
    data['brief']['animation_requested']=False
    data['brief']['editable_requested']=(which=='A')
    return data

class StyleFirstTests(unittest.TestCase):
    def test_new_template_valid(self):
        self.assertEqual(mod.validate(sample()),[])
    def test_can_not_select_branch_before_eight_images(self):
        d=sample()
        d['workflow_branch']='B'
        d['gates']['branch_selected']=True
        self.assertTrue(any('branching prohibited' in e for e in mod.validate(d)))
    def test_eight_images_gate(self):
        d=sample('style_await_selection')
        self.assertTrue(mod.validate(d))
        self.assertEqual(mod.validate(with_style(d)),[])
    def test_route_requires_style_selection(self):
        d=with_style(sample('route'))
        self.assertTrue(any('selected_style_id' in e for e in mod.validate(d)))
        self.assertEqual(mod.validate(selected(d)),[])
    def test_a_after_style_no_second_style_gate(self):
        d=branch(sample('pilot'),'A')
        self.assertEqual(mod.validate(d),[])
    def test_b_after_style_still_has_quality_gate(self):
        d=branch(sample('b_await_confirmation'),'B')
        self.assertTrue(any('quality previews' in e for e in mod.validate(d)))
        p=d['b_previews']
        p.update(slide_id='slide-02',B1='previews/B1.png',B2='previews/B2.png',prompt_base='选定风格03')
        p['prompt_B1']=p['prompt_base']
        p['prompt_B2']=p['prompt_base']+'\n'+mod.B2_QUALITY_CONSTRAINT
        d['gates']['b_previews_generated']=True
        self.assertEqual(mod.validate(d),[])
    def test_b_does_not_accept_early_variant_confirmation(self):
        d=branch(sample('b_preview'),'B')
        d['b_generation_mode']='both'
        d['gates']['b_variant_confirmed']=True
        self.assertTrue(any('cannot select variant' in e for e in mod.validate(d)))
    def test_b_requires_eight_images_even_after_branch(self):
        d=branch(sample('b_preview'),'B')
        d['styleboards'].pop()
        self.assertTrue(any('eight distinct' in e for e in mod.validate(d)))
    def test_a_deliver_rejects_missing_files(self):
        d=branch(sample('delivered'),'A')
        d['gates']['artwork_approved']=True
        self.assertTrue(any('delivered requires' in e for e in mod.validate(d)))

if __name__=='__main__':
    unittest.main()
