import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('charts',Path(__file__).resolve().parents[3]/'hb/core/charts.py')
charts=importlib.util.module_from_spec(spec);spec.loader.exec_module(charts)
ns={'s':'http://www.w3.org/2000/svg'}
class Charts(unittest.TestCase):
 def svg(self,**data):return ET.fromstring(charts.render_chart(data))
 def test_waterfall_closes_and_float_bars_follow_cumulative_totals(self):
  root=self.svg(type='waterfall',start=25,changes=[{'label':'growth','value':12},{'label':'cost','value':-5}],expected_total=32)
  bars=root.findall('s:rect',ns)
  self.assertEqual([(float(b.attrib['data-start']),float(b.attrib['data-end'])) for b in bars],[(0,25),(25,37),(37,32),(0,32)])
  for b in bars:self.assertGreaterEqual(float(b.attrib['height']),0)
  with self.assertRaisesRegex(ValueError,'does not close'):self.svg(type='waterfall',start=25,changes=[{'label':'cost','value':-5}],expected_total=32)
 def test_bar_uses_zero_for_both_signs(self):
  bars=self.svg(type='bar',labels=['decrease','increase'],values=[-10,20]).findall('s:rect',ns)
  neg,pos=bars;zero=float(neg.attrib['data-zero'])
  self.assertAlmostEqual(float(neg.attrib['x'])+float(neg.attrib['width']),zero,places=2)
  self.assertAlmostEqual(float(pos.attrib['x']),zero,places=2)
  self.assertAlmostEqual(float(pos.attrib['width'])/float(neg.attrib['width']),2,places=3)
 def test_stacked_rejects_invalid_totals_and_negative_values(self):
  for vals in ([30,90],[-10,100]):
   with self.assertRaises(ValueError):self.svg(type='stacked',labels=['A','B'],series=[{'name':'part','values':vals}])
 def test_percent_geometry_matches_values(self):
  root=self.svg(type='stacked',labels=['A'],series=[{'name':'one','values':[25]},{'name':'two','values':[75]}])
  a,b=root.findall('s:rect',ns);self.assertAlmostEqual(float(b.attrib['width'])/float(a.attrib['width']),3)
 def test_nonfinite_boolean_mismatched_empty_values_are_rejected(self):
  for vals in ([float('nan')],[float('inf')],[True],[],[1,2]):
   with self.assertRaises(ValueError):self.svg(type='bar',labels=['A'],values=vals)
  with self.assertRaises(ValueError):self.svg(type='bar',labels=[],values=[])
 def test_line_default_zero_and_explicit_range_validation(self):
  root=self.svg(type='line',labels=['A','B'],series=[{'name':'Revenue','values':[80,100]}])
  self.assertIn('0',[t.text for t in root.findall('s:text',ns)])
  with self.assertRaises(ValueError):self.svg(type='line',labels=['A','B'],series=[{'name':'R','values':[80,100]}],range=[90,110])
 def test_text_is_escaped_and_title_ids_are_valid(self):
  svg=charts.render_chart({'type':'bar','title':'<script>&','labels':['A & B'],'values':[2],'id':'safe'})
  self.assertNotIn('<script>',svg);self.assertIn('&lt;script&gt;&amp;',svg)
  self.assertEqual(ET.fromstring(svg).find('s:title',ns).attrib['id'],'safe-title')
  with self.assertRaises(ValueError):self.svg(type='bar',labels=['A'],values=[1],id='bad" onclick=')
 def test_waterfall_crossing_zero_is_finite_and_keeps_negative_total(self):
  bars=self.svg(type='waterfall',start=5,changes=[{'label':'loss','value':-12}],expected_total=-7).findall('s:rect',ns)
  self.assertEqual(float(bars[-1].attrib['data-end']),-7)
  self.assertTrue(all(float(b.attrib['height'])>=0 for b in bars))
 def test_small_segments_and_too_small_canvas_require_an_author_decision(self):
  with self.assertRaises(ValueError):self.svg(type='stacked',labels=['A'],series=[{'name':'small','values':[1]},{'name':'large','values':[99]}])
  with self.assertRaises(ValueError):self.svg(type='bar',labels=['A'],values=[1],width=400)
 def test_malformed_inputs_and_derived_overflow_fail_cleanly(self):
  for data in ([], {'type':'line','labels':['a','b'],'series':[42]},
               {'type':'waterfall','start':2,'changes':[3]},
               {'type':'bar','labels':['a','b'],'values':[-1e308,1e308]},
               {'type':'stacked','labels':['a'],'percent':False,'series':[{'name':'a','values':[1e308]},{'name':'b','values':[1e308]}]}):
   with self.assertRaises(ValueError):charts.render_chart(data)
 def test_native_labels_remain_visible_ordinary_text_with_same_values(self):
  data={'type':'waterfall','start':10,'changes':[{'label':'A & B','value':-3}],'expected_total':7}
  standalone=ET.fromstring(charts.render_chart(data))
  figure=ET.fromstring(charts.render_figure(data))
  self.assertEqual([t.text for t in standalone.findall('s:text',ns)],[p.text for p in figure.findall('p')])
  self.assertEqual(len(figure.findall('.//s:text',ns)),0)
  self.assertTrue(all(p.attrib['data-role']=='key' for p in figure.findall('p')))
if __name__=='__main__':unittest.main()
