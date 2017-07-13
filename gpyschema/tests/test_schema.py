# from __future__ import absolute_import

import unittest
import sys
import HtmlTestRunner

from gpyschema.gpyschema import GpySchema, SchemaError, ValidationError

class TestSchema(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print 'test begin\n'
    
    @classmethod
    def tearDownClass(self):
        print '\ntest complete'

    def test_schema_not_none(self):
        with self.assertRaises(SchemaError):
            GpySchema(None).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({}).check_schema()

    def test_schema_type(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'something'}).check_schema()
    
    def test_schema_ref(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': ''}).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': []}).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': 'sss'}).check_schema()

class TestValidator(unittest.TestCase):

    def test_object(self):
        self.assertEqual(GpySchema().validate({'type': 'object'}, {}), True)

        with self.assertRaises(ValidationError):
            GpySchema().validate({'type': 'object', 'minProperties': 1}, {})

        with self.assertRaises(ValidationError):
            GpySchema().validate({'type': 'object', 'maxProperties': 0}, {'a':'', 'b': ''})
        
        # patternProperties
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'object', 
                'patternProperties': {
                    'xx.*xx': {'type': 'string'}
                }
            }, {'xxdkfjkjxx': 1})

        # additionalProperties
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'object', 
                'additionalProperties': {'type': 'string'}
            }, {'xxdkfjkjxx': 1})
        
        # required
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'object', 
                'properties': {'b': {'type': 'string'}},
                'required': ['b']
            }, {'a': 1})
        
        
        

        

        
        




if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='.'))