# gpyschema

轻量的python数据格式校验方法

使用JSON schema规则进行校验, 支持多数draft-4规则


## 使用方法
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
        'order': {'type': 'integer'},
        'permission2': {'type': 'string', 'format': 'json'},
        'permission': {'type': 'object',
            'properties': {
                'c': {'type': 'array', 'minItems': 1},
                'r': {'type': 'array', 'minItems': 1},
                'u': {'type': 'array', 'minItems': 1},
                'd': {'type': 'array', 'minItems': 1},
            },
            'required': ['c', 'r', 'u', 'd']
        }
    },
    'required': ['name', 'cname', 'category', 'icon', 'visible', 'desc', 'order',]
}
data = {
    'category': u'基础资源管理', 
    'name': u'ip', 
    'permission': {"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]},
    'permission2': '{"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]1}',
    'default': 1, 
    'order': 11L, 
    'visible': True, 
    'cname': u'ip地址段', 
    'icon': u'glyphicon glyphicon-sort', 
    # 'id': 23L, 
    'desc': u''
}
try:
    data_validate(schema, data, strict=True)
    print '验证通过'
except (SchemaError, ValidationError) as e:
    print e
```
