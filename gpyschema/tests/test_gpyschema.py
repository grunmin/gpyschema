# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')

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

    def test_not_none(self):
        with self.assertRaises(SchemaError):
            GpySchema(None).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({}).check_schema()

    def test_type(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'something'}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'something': 'something'}).check_schema()
    
    def test_ref(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': ''}).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': []}).check_schema()

        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', '$ref': 'sss'}).check_schema()

    def test_message(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'message': []}).check_schema()
    
    def test_enum(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'enum': {}}).check_schema()

    def test_not(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'not': {'bbb': None}}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'not': [{'bbb': None}]}).check_schema()

    def test_anyOf(self):
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'anyOf': {'bbb': None}}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'anyOf': [{'bbb': None}]}).check_schema()
        self.assertIsNone(GpySchema({'type': 'object', 'anyOf': [{'type': 'object'}]}).check_schema())
    
    def test_object(self):
        # properties
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'properties': []}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'properties': {}}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'properties': {'a': 'string'}}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'properties': {'': 'string'}}).check_schema()
        self.assertIsNone(GpySchema({'type': 'object', 'properties': {'a': {'type': 'string'}}}).check_schema())

        # lenfth of properties
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'maxProperties': {}}).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({'type': 'object', 'minProperties': []}).check_schema()
        
        # required
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'properties': {
                    'a': {'type': 'string'}
                },
                'required': 'a'
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'properties': {
                    'a': {'type': 'string'}
                },
                'required': ['b']
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'object', 
                'properties': {
                    'a': {'type': 'string'}
                },
                'required': ['a']
            }).check_schema())
        
        # patternProperties
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'patternProperties': {
                },
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'patternProperties': {
                    'xr(': {'type': 'string'}
                },
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'patternProperties': {
                    4: {'type': 'string'}
                },
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'patternProperties': {
                    'xr': 'string'
                },
            }).check_schema()
        
        # additionalProperties
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'additionalProperties': True,
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'object', 
                'additionalProperties': {
                    'type': 's'
                }
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'object', 
                'additionalProperties': {
                    'type': 'string'
                }
            }).check_schema())
    
    def test_array(self):
        # items
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'items': True,
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'items': [],
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'items': {},
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'items': [{}],
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'array', 
                'items': {
                    'type': 'string'
                }
            }).check_schema())
        self.assertIsNone(GpySchema({
                'type': 'array', 
                'items': [{
                    'type': 'string'
                }]
            }).check_schema())
        
        # length of items
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'maxItems': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'maxItems': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'array', 
                'maxItems': 2,
            }).check_schema())
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'minItems': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'minItems': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'array', 
                'minItems': 2,
            }).check_schema())
        
        # uniqueItems
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'uniqueItems': '2',
            }).check_schema()
        
        # additionalItems
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'additionalItems': '2',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'array', 
                'additionalItems': [{'type': 'string'}],
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'array', 
                'additionalItems': {'type': 'string'},
            }).check_schema())

    def test_string(self):
        # length
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'maxLength': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'maxLength': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'string', 
                'maxLength': 2,
            }).check_schema())
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'minLength': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'minLength': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'string', 
                'minLength': 2,
            }).check_schema())
    
        # pattern
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'pattern': '2(',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'pattern': 2,
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'string', 
                'pattern': '2[1,2]',
            }).check_schema())

        # rformat
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'string', 
                'format': 'something',
            }).check_schema()
        for i in ['email', 'ipv4', 'alpha', 'alnum', 'digit','numeric', 'date', 'datetime', 'price', 'json', 'regex']:
            self.assertIsNone(GpySchema({
                    'type': 'string', 
                    'format': i,
                }).check_schema())
    
    def test_integer_and_number(self):
        # length
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'integer', 
                'maximum': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'integer', 
                'maximum': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'integer', 
                'maximum': 2,
            }).check_schema())
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'integer', 
                'minimum': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'integer', 
                'minimum': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'integer', 
                'minimum': 2,
            }).check_schema())
        

        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'number', 
                'maximum': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'number', 
                'maximum': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'number', 
                'maximum': 2,
            }).check_schema())
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'number', 
                'minimum': '',
            }).check_schema()
        with self.assertRaises(SchemaError):
            GpySchema({
                'type': 'number', 
                'minimum': '2',
            }).check_schema()
        self.assertIsNone(GpySchema({
                'type': 'number', 
                'minimum': 2,
            }).check_schema())
    

            




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
    
    def test_enum(self):
        with self.assertRaises(ValidationError):
            GpySchema().validate({
                'type': 'array',
                'items': {'enum': [1, 2, '3']}
            }, (1, 2, 3))
        self.assertEqual(GpySchema().validate({
                'type': 'array',
                'items': {'enum': [1, 2, '3']}
            }, [1, 2, '3']), True)
    
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

if __name__ == '__main__':
    unittest.main()