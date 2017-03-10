# coding: utf-8
import sys
import traceback
from jsonschema import validate, Draft4Validator, ValidationError, SchemaError

class RequestValidationError(Exception):

    def __init__(self, value):
        Exception.__init__(self, value)


class RequestValidation(object):

    def __init__(self):
        self.schema_dict = {}
        self.__i18n_validator_map()
        self.__i18n_type_map()

    def validate(self, schema, data, i18n='cn'):
        validator = self.__get_validator(schema)
        try:
            validator.validate(data)
        except ValidationError as e:
            message = self.__message_i18n(e, i18n)
            raise RequestValidationError(message)


    def __get_validator(self, schema):
        schema_text = str(schema)
        if self.schema_dict.get(schema_text) is None:
            try:
                Draft4Validator.check_schema(schema)
            except SchemaError as e:
                print sys.stderr, traceback.print_exc()
                raise RequestValidationError('系统配置错误, 请联系管理员')
            validator = Draft4Validator(schema)
            self.schema_dict[schema_text] = validator
        else:
            validator = self.schema_dict.get(schema_text)
        return validator

    def __message_i18n(self, error, i18n):
        for i in dir(error):
            if i.startswith('_'):
                continue
            print i, getattr(error, i)

        if i18n != 'cn':
            return error.message

        schema = error.schema
        path = error.path
        msg = schema.get('message')
        cname = schema.get('title') or (path[-1] if path else "")
        validator = error.validator

        s_value = error.validator_value
        v_value = error.instance
        s_type = self.type_map.get(str(s_value), '')
        v_type = self.type_map.get(str(type(v_value))[7:-2], '')

        if validator == 'required':
            s_value = ','.join([i for i in schema['required'] if i not in v_value.keys()])
        if validator == 'additionalProperties':
            s_value = ','.join([i for i in v_value.keys() if i not in schema['required']])

        message = msg.format(
            name=cname, 
            title=cname, 
            key=cname, 
            value=v_value, 
            data=v_value, 
            instance=v_value
        ) if msg else self.validator_map[validator].format(
            cname=cname, 
            s_value=s_value, 
            s_type=s_type, 
            v_value=v_value, 
            v_type=v_type
        )

        return message

    def __i18n_validator_map(self):

        self.validator_map = {
            '': '',
            'type': '{cname} 只接收 {s_type}, 您输入的是 {v_type}',
            'not': '{cname} 的值不能是 {v_value}',
            'enum': '{cname} 值 {v_value} 不合理',

            'maxLength': '{cname} 长度不能大于 {s_value}',
            'minLength': '{cname} 长度不能小于 {s_value}',
            'pattern': '{cname} ',

            'maximum': '{cname} 值不能大于 {s_value}',
            'minimum': '{cname} 值不能小于 {s_value}',

            'maxItems': '{cname} 个数不能大于 {s_value}',
            'minItems': '{cname} 个数不能小于 {s_value}',
            'items': '',
            'uniqueItems': '{cname} 中的元素不能重复',

            'properties': '{cname} ',
            'maxProperties': '{cname} ',
            'minProperties': '{cname} ',
            'additionalProperties': '{cname} 中存在无效属性 {s_value}',

            'required': '{cname} 缺少必需属性 {s_value}',
            'anyOf': '{cname} ',
        }

    def __i18n_type_map(self):

        self.type_map = {
            'boolean': '布尔值',
            'integer': '整数',
            'number': '数字',
            'string': '字符',
            'array': '列表', 
            'object': '对象(字典)', 
            'null': '空值', 
            'int': '整数',
            'float': '小数', 
            'str': '字符',
            'unicode': '字符',
            'list': '列表',
            'dict': '对象(字典)',
            'NoneType': '空值',
            'bool': '布尔值',
        }

rv = RequestValidation()
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
        'order': {'title':'顺序', 'type': 'integer', 'not': {'type': 'integer', 'enum': [12,13]}},
        'id': {'enum': [1, 23, 3]},
        'permission2': {'type': 'string', 'format': 'json'},
        'permission': {'type': 'object',
            'properties': {
                'c': {'type': 'array', 'minItems': 1, 'items': {'type': 'string'}},
                'r': {'type': 'array', 'minItems': 1},
                'u': {'type': 'array', 'minItems': 1},
                'd': {'type': 'array', 'minItems': 1},
            },
            'required': ['c', 'r', 'u', 'd'],
            'additionalProperties':False,
        },
        # 'schema': {'type': 'object', 
        #     'properties': {
        #         'c': {'type': 'array', 'minItems': 1},
        #     },
        #     'minProperties': 1,
        #     'patternProperties': {
        #         '^[a-zA-Z]+\.[a-zA-Z]+$': {'type': 'array', 'minItems': 1}
        #     },
        #     'additionalProperties': False,
        # },
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
    'permission': {"c": ["admin", []], "r": ["admin"], "u": ["admin"], "d": ["admin"]},
    'permission2': '{"c": ["admin"], "r": ["admin"], "u": ["admin"], "d": ["admin"]}',
    'default': 1, 
    'order': 3, 
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
            'any': '1'
        }
    }
}
# rv.validate({"title": "测试", "maxItems": 2}, [2, 3, 4])
rv.validate(schema, data)
