# gpyschema

轻量的python数据格式校验方法

使用JSON schema规则进行校验, 支持多数draft-4规则

## Supported property

#### Type-specific keywords

- boolean
- integer
- number
- string
- object
- array


#### Generic keywords

- title
- enum
- not
- type

#### Object keywords

- properties
- maxProperties
- minProperties
- required
- additionalProperties

#### Array keywords

- items
- maxItems
- minItems
- uniqueItems

#### String keywords

- maxLength
- minLenght
- pattern

#### Number&Integer

- maximum
- minimum

#### Custom String

- ipv4
- alnum
- alpha
- email
- price
- date
- datetime
- json
- regex

#### Combining schemas

- anyOf

#### Nested Schema Supported


## TODO

- add `dependencies` support
- full `Combining schemas` support


## Example

```python
from gpyschema import ValidationError, SchemaError, data_validate
schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'maxLength': 20, 'minLength': 2, 'format': 'alpha' },
        'cname': {'type': 'string', 'maxLength': 20, 'minLength': 2 },
        'category': {'type': 'string', 'maxLength': 20, 'minLength': 2, 'title': '分类' },
        'icon': {'type': 'string', 'maxLength': 50, 'minLength': 2},
        'visible': {'type': 'boolean'},
        'desc': {'type': 'string', 'maxLength': 100, 'minLength': 0, 'title': '描述信息'},
        'default': {'type': 'integer'},
        'order': {'type': 'integer', 'not': {'type': 'integer', 'enum': [12]}},
        'id': {'enum': [1, 23, 3]},
        'permission2': {'type': 'string', 'format': 'json'},
        'permission': {'type': 'object',
            'properties': {
                'c': {'type': 'array', 'minItems': 1},
                'r': {'type': 'array', 'minItems': 1},
                'u': {'type': 'array', 'minItems': 1},
                'd': {'type': 'array', 'minItems': 1},
            },
            'required': ['c', 'r', 'u', 'd']
        },
        'schema': {'type': 'object', 
            'properties': {
                '_and': '{{Schema}}',
                'c': {'type': 'array', 'minItems': 1},
            },
            'minProperties': 1,
            'patternProperties': {
                '^[a-zA-z]+$': '{{Schema}}',
                '^[a-zA-Z]+\.[a-zA-Z]+$': {'type': 'array', 'minItems': 1}
            },
            'additionalProperties': False,
        },
        'any': {
            'anyOf': [
                {'type': 'string'},
                {'type': 'integer'}
            ]
        }
    },
    'required': ['name', 'cname', 'category', 'icon', 'visible', 'desc', 'order', 'id', 'any']
}
data = {
    'category': u'基础资源管理', 
    'name': u'ip', 
    'permission': {"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]},
    'permission2': '{"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]}',
    'default': 1, 
    'order': 1, 
    'visible': True, 
    'cname': u'ip地址段', 
    'icon': u'glyphicon glyphicon-sort', 
    'id': 23L, 
    'desc': u'',
    'any': '111',
    'schema': {
        'c': {
            'category': u'基础资源管理', 
            'name': u'ip', 
            'permission': {"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]},
            'permission2': '{"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]}',
            'default': 1, 
            'order': 1, 
            'visible': True, 
            'cname': u'ip地址段', 
            'icon': u'glyphicon glyphicon-sort', 
            'id': 23L, 
            'desc': u'',
            'any': 1.1
        }
    }
}

try:
    data_validate(schema, data, ref={'Schema': schema})
    print 'validation pass'
except (SchemaError, ValidationError) as e:
    print e
```
