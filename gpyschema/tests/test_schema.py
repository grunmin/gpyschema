# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import unittest
import sys

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

    def test_not(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'not': {'type': 'number'}}
            }, [2])
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'not': {'type': 'string', 'enum': ['1']}}
            }, ['1'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'not': {'type': 'string', 'enum': ['1']}}
            }, ['2']), True)
    
    def test_anyOf(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'anyOf': [{'type': 'number'}]}
            }, [2, '3'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'anyOf': [{'type': 'number'}, {'type': 'object'}]}
            }, [2, {}]), True)
        

    
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
        
    def test_array(self):
        # strict
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array', 
            }, (1,2,3))
        self.assertEqual(GpySchema().validate({'type': 'array'}, (1,2,3), strict=False), True)
        
        # maxItems
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'maxItems': 0
            }, [1, 2, 3])
        
        # minItems
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array', 
                'minItems': 4
            }, [1, 2, 3])

        # uniqueItems
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array', 
                'uniqueItems': True
            }, [1, 1, 2, 3])
        
        # items
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {
                    'type': 'object'
                }
            }, [1, 2, 3])
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}]
            }, [1, 2, 3])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}]
            }, ['1', 2]), True)

        # enum
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'enum': [1, 2, '3']}
            }, (1, 2, 3))
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'enum': [1, 2, '3']}
            }, [1, 2, '3']), True)


        # additionalItems
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'additionalItems': {
                    'type': 'object'
                }
            }, [1, 2, 3])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}],
                'additionalItems': {'type': 'string'}
            }, ['1', 2, '3']), True)

        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string'},
                'additionalItems': {'type': 'number'}
            }, ['1', 2])
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}],
                'additionalItems': {
                    'type': 'object'
                }
            }, ['1', 2, '3'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}],
            }, ['1', 2, '3']), True)
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'number'}],
                'additionalItems': False
            }, ['1', 2, '3'])
    
    def test_string(self):
        # type
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string'}
            }, [2])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string'}
            }, ['2']), True)
        
        # length
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'maxLength': 0}
            }, ['2'])
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'minLength': 2}
            }, ['2'])
        
        # pattern
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'pattern': 'xx.xx'}
            }, ['xx3'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'pattern': 'xx.xx'}
            }, ['xx2xx']), True)
        
        # format
        # alpha
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'alpha'}
            }, ['2x'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'alpha'}
            }, ['x']), True)
        # alnum
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'alnum'}
            }, ['2x#'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'alnum'}
            }, ['x2']), True)
        # digit
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'digit'}
            }, ['2x'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'digit'}
            }, ['244']), True)
        # numeric
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'numeric'}
            }, ['2x4'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'numeric'}
            }, ['⅕']), True)
        # email
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'email'}
            }, ['444@ff'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'email'}
            }, ['333@33.com']), True)
        # ipv4
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'ipv4'}
            }, ['1.1.1.268'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'ipv4'}
            }, ['1.1.1.1']), True)
        # date
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'date'}
            }, ['2011-21-11'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'date'}
            }, ['2011-01-01']), True)
        # datetime
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'datetime'}
            }, ['2011-01-01 22:22:2:'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'datetime'}
            }, ['2011-01-01 22:22:22']), True)
        # json
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'json'}
            }, ['{12: "21"}'])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'json'}
            }, ['{"11": 11}']), True)
        # regex
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'regex'}
            }, ['2x#('])
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'type': 'string', 'format': 'regex'}
            }, ['2x[1,2]']), True)

    def test_boolean(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'boolean',
            }, 0)
        self.assertEqual(GpySchema().validate({
                'type': 'boolean',
            }, 0, strict=False), True)
    
    def test_interger_and_number(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'integer',
            }, '0')
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'integer',
            }, 0.1)
        self.assertEqual(GpySchema().validate({
                'type': 'integer',
            }, '0', strict=False), True)

        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'number',
            }, '0.1')
        self.assertEqual(GpySchema().validate({
                'type': 'number',
            }, '0.1', strict=False), True)
        self.assertEqual(GpySchema().validate({
                'type': 'number',
            }, 0.1), True)
    
    def test_null(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'null',
            }, '')
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'null',
            }, [])
        self.assertEqual(GpySchema().validate({
                'type': 'null',
            }, '', strict=False), True)
        self.assertEqual(GpySchema().validate({
                'type': 'null',
            }, None), True)
