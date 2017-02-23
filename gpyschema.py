# -*- coding:utf-8 -*-
import re
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import simplejson as json
except ImportError:
    import json


class GpySchemaError(Exception):
    def __init__(self, message, cause='', schema=None, instance=None):
        super(GpySchemaError, self).__init__(message, cause, schema, instance)
        self.message = message
        self.cause = cause
        self.schema = schema
        self.instance = instance

class ValidationError(GpySchemaError):
    pass

class SchemaError(GpySchemaError):
    pass

def data_validate(schema, data, top=True, name='', ref=None):
    
    if isinstance(schema, basestring) and schema.startswith('#'):
        if not ref.get(schema[1:]):
            raise SchemaError('无效的数据模型:{0}'.format('找不到指定的schema'))
        data_validate(ref.get(schema[1:]), data, top=False, name=name)
        return True


    if not isinstance(schema, dict) or not schema:
        raise SchemaError('无效的数据模型:{0}'.format('schema必须是非空字典'))


    rtype = schema.get('type')
    title = schema.get('title', '') or name
    enum = schema.get('enum')
    rnot = schema.get('not')
    anyOf = schema.get('anyOf')
    message = schema.get('message')

    if enum and not isinstance(enum, list):
        raise SchemaError('无效的数据模型:{0}'.format('枚举值必须通过列表传入'))
    if enum and data not in enum:
        raise ValidationError(message or '{0} 值必须在指定区域内, 该区域是({1})'.format(title, ','.join(str(i) for i in enum)), 'enum')

    if rnot and not isinstance(rnot, dict):
        raise SchemaError('无效的数据模型:{0}'.format('not只能是字典'))
    if rnot:
        try:
            correct = data_validate(rnot, data, top=False, name=title, ref=ref)
        except ValidationError:
            correct = None
        if correct:
            raise ValidationError(message or '{0} 值 {1} 不被允许'.format(title, str(data)), 'not')

    if anyOf and not isinstance(anyOf, list):
        raise SchemaError('无效的数据模型:{0}'.format('anyOf只能是列表'))
    if anyOf:
        correct = None
        for rschema in anyOf:
            if correct is not None:
                continue
            try:
                correct = data_validate(rschema, data, top=False, name=title, ref=ref)
            except ValidationError:
                correct = None
        if correct is None:
            raise ValidationError(message or '{0} 值 格式错误'.format(title), 'anyOf')
        return True

    if rtype == 'object':
        if not isinstance(data, dict):
            raise ValidationError(message or '{0} 值必须是字典, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')

        properties = schema.get('properties')
        if not properties or not isinstance(properties, dict):
            raise SchemaError('无效的数据模型:{0}'.format('object必须有properties定义'))
        maxProperties = schema.get('maxProperties')
        minProperties = schema.get('minProperties')
        dependencies = schema.get('dependencies')
        patternProperties = schema.get('patternProperties')
        additionalProperties = schema.get('additionalProperties')
        required = schema.get('required')

        if maxProperties and not isinstance(maxProperties, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maxProperties必须是数字'))
        if minProperties and not isinstance(minProperties, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minProperties必须是数字'))
        if required and not isinstance(required, list):
            raise SchemaError('无效的数据模型:{0}'.format('required必须是列表'))
        if required and [i for i in required if i not in properties.keys()]:
            raise SchemaError('无效的数据模型:{0}'.format('required中的元素必须在properties中定义'))
        if additionalProperties and not isinstance(additionalProperties, dict):
            raise SchemaError('无效的数据模型:{0}'.format('additionalProperties必须是字典'))
        if patternProperties and not isinstance(patternProperties, dict):
            raise SchemaError('无效的数据模型:{0}'.format('patternProperties必须是字典'))
        if patternProperties:
            for pattern, value in patternProperties.items():
                if not isinstance(pattern, basestring):
                    raise SchemaError('无效的数据模型:{0}'.format('无法识别正则式'))
                if not (isinstance(value, basestring) and value.startswith('#') and ref.get(value[1:])) and not (isinstance(value, dict) and value):
                    raise SchemaError('无效的数据模型:{0}'.format('属性模式描述信息必须是有效的schema'))
                try:
                    rule = re.compile(pattern)
                except:
                    raise SchemaError('无效的数据模型:{0}'.format('无法识别属性模式的正则式'))


        if maxProperties and len(data) > maxProperties:
            raise ValidationError(message or '{0} 属性数量不能大于{1}'.format(title, str(maxProperties)), 'maxProperties')
        if minProperties and len(data) < minProperties:
            raise ValidationError(message or '{0} 属性数量不能小于{1}'.format(title, str(minProperties)), 'minProperties')
        if required:
            miss = [i for i in required if i not in data.keys()]
            if miss:
                raise ValidationError(message or '{0}必须包含属性{1}'.format(title, ','.join(miss)), 'required')

        patternList = patternProperties.keys() if patternProperties else []
        for key, value in data.items():
            if patternList:
                matchList = [p for p in patternList if re.match(p, key)]
                for p in matchList:
                    data_validate(patternProperties[p], value, top=False, name=key, ref=ref)
                if matchList:
                    continue
            if additionalProperties is None and key not in properties.keys():
                continue
            if additionalProperties is False and key not in properties.keys():
                raise ValidationError(message or '{0}不是有效的属性名'.format(str(key)), 'additionalProperties')
            if additionalProperties and key not in properties.keys():
                data_validate(additionalProperties, value, top=False, name=key, ref=ref)
                continue
            data_validate(properties[key], value, top=False, name=key, ref=ref)
        return True

    elif rtype == 'array':
        if not isinstance(data, (list, tuple)):
            raise ValidationError(message or '{0} 值必须是列表或元组类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')

        items = schema.get('items')
        if items and not isinstance(items, dict):
            raise SchemaError('无效的数据模型:{0}'.format('items必须是字典'))
        maxItems = schema.get('maxItems')
        minItems = schema.get('minItems')
        uniqueItems = schema.get('uniqueItems')
        if maxItems and not isinstance(maxItems, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maxItems必须是数字'))
        if minItems and not isinstance(minItems, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minItems必须是数字'))
        if uniqueItems and not isinstance(uniqueItems, bool):
            raise SchemaError('无效的数据模型:{0}'.format('uniqueItems必须是布尔值'))
        if maxItems and len(data) > maxItems:
            raise ValidationError(message or '{0} 元素数量不能大于{1}'.format(title, str(maxItems)), 'maxItems')
        if minItems and len(data) < minItems:
            raise ValidationError(message or '{0} 元素数量不能小于{1}'.format(title, str(minItems)), 'minItems')
        if uniqueItems:
            used = []
            unique = [used.append(x) for x in data if x not in used]
            if len(unique) != len(data):
                raise ValidationError(message or '{0} 元素必须唯一'.format(title), 'uniqueItems')
        if not items:
            return True
        for i in data:
            data_validate(items, i, name=title, top=False, ref=ref)

        return True

    elif top:
        raise SchemaError('无效的数据模型:{0}'.format('只能是列表或字典'))



    if rtype == 'string':
        if not isinstance(data, basestring):
            raise ValidationError(message or '{0} 值必须是字符类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]))
        maxLength = schema.get('maxLength')
        minLength = schema.get('minLength')
        pattern = schema.get('pattern')
        rformat = schema.get('format')

        if maxLength and not isinstance(maxLength, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maxLength必须是数字'))
        if minLength and not isinstance(minLength, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minLength必须是数字'))
        if pattern:
            if not isinstance(pattern, basestring):
                raise SchemaError('无效的数据模型:{0}'.format('无法识别正则式'))
            try:
                rule = re.compile(pattern)
            except:
                raise SchemaError('无效的数据模型:{0}'.format('无法识别正则式'))
        if rformat and rformat not in ['email', 'ipv4', 'alpha', 'alnum', 'date', 'datetime', 'price', 'json', 'regex']:
            raise SchemaError('无效的数据模型:{0}'.format('不支持的formatter'))


        if maxLength and len((unicode(str(data),"utf-8"))) > maxLength:
            raise ValidationError(message or '{0} 值长度不能大于{1}'.format(title, str(maxLength)), 'maxLength')
        if minLength and len((unicode(str(data),"utf-8"))) < minLength:
            raise ValidationError(message or '{0} 值长度不能小于{1}'.format(title, str(minLength)), 'minLength')
        if pattern and  not re.match(rule, data):
            raise ValidationError(message or '{0} 值不合理'.format(title), 'pattern')

        if not rformat:
            return True

        if rformat == 'alpha' and not data.isalpha():
            raise ValidationError(message or '{0} 值要求只包含英文字母'.format(title), 'format')
        if rformat == 'alnum' and not data.isalnum():
            raise ValidationError(message or '{0} 值要求只包含数字'.format(title), 'format')
        if rformat == 'email' and not re.match('[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$', data):
            raise ValidationError(message or '{0} 值要求邮箱格式'.format(title), 'format')
        if rformat == 'ipv4' and not re.match('^((0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])\.){3}(0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])$', data):
            raise ValidationError(message or '{0} 值要求IPv4格式'.format(title), 'format')
        if rformat == 'price' and not re.match('^[0-9]{1,8}(\.[0-9]{1,2}){0,1}$', data):
            raise ValidationError(message or '{0} 值要求只包含数字和小数点'.format(title), 'format')
        if rformat == 'date':
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d')
            except ValueError:
                raise ValidationError(message or '{0} 值要求日期格式:YYYY-mm-dd'.format(title), 'format')
        if rformat == 'datetime':
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError(message or '{0} 值要求日期+时间格式:YYYY-mm-dd HH:MM:SS'.format(title), 'format')
        if rformat == 'json':
            try:
                json.loads(data)
            except ValueError:
                raise ValidationError('{0} 值要求json格式'.format(title), 'format')
        if rformat == 'regex':
            try:
                re.compile(data)
            except:
                raise ValidationError('{0} 值不是有效的正则式'.format(title), 'format')

        return True

    if rtype == 'boolean':
        if not isinstance(data, bool):
            raise ValidationError(message or '{0} 值必须是布尔类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')
        return True

    if rtype in ['integer', 'number']:
        if rtype == 'integer' and not isinstance(data, (int, long)):
            raise ValidationError(message or '{0} 值必须是整数, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')

        if rtype == 'number' and not isinstance(data, (int, long, float, complex)):
            raise ValidationError(message or '{0} 值必须是数字, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')

        maximum = schema.get('maximum')
        minimum = schema.get('minimum')
        if maximum and not isinstance(maximum, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maximum必须是数字'))
        if minimum and not isinstance(minimum, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minimum必须是数字'))
        if maximum and data > maximum:
            raise ValidationError(message or '{0} 值不能大于{1}'.format(title, str(maximum)), 'maximum')
        if minimum and data < minimum:
            raise ValidationError(message or '{0} 值不能小于{1}'.format(title, str(minimum)), 'minimum')

        return True

    if rtype == 'null':
        if data is not None:
            raise ValidationError(message or '{0} 值必须是None, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type')
        return True

if __name__ == '__main__':
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
            'order': {'type': 'integer', 'not': {'type': 'integer', 'enum': [12]}, 'message': '请输入整数值'},
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
                    '_and': '#Schema',
                    'c': {'type': 'array', 'minItems': 1},
                },
                'minProperties': 1,
                'patternProperties': {
                    '^[a-zA-z]+$': '#Schema',
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
        'order': '1', 
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

    try:
        data_validate(schema, data, ref={'Schema': schema})
        print '验证通过'
    except (SchemaError, ValidationError) as e:
        print e.message, e.cause