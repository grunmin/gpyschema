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



class ValidationError(Exception):

    def __init__(self, value):
        Exception.__init__(self, value)

class SchemaError(Exception):

    def __init__(self, value):
        Exception.__init__(self, value)

def data_validate(schema, data, top=True, name='', strict=True):

    if not isinstance(schema, dict):
        raise SchemaError('无效的数据模型')

    rtype = schema.get('type')
    title = schema.get('title', '') or name
    enum = schema.get('enum')

    if rtype == 'object':
        properties = schema.get('properties')
        if not properties or not isinstance(properties, dict):
            raise SchemaError('无效的数据模型')
        maxProperties = schema.get('maxProperties')
        minProperties = schema.get('minProperties')
        dependencies = schema.get('dependencies')
        required = schema.get('required')

        if maxProperties and not isinstance(maxProperties, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maxProperties必须是数字'))
        if minProperties and not isinstance(minProperties, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minProperties必须是数字'))
        if required and not isinstance(required, list):
            raise SchemaError('无效的数据模型:{0}'.format('required必须是列表'))
        if required and [i for i in required if i not in properties.keys()]:
            raise SchemaError('无效的数据模型:{0}'.format('required中的元素必须在properties中定义'))

        if maxProperties and len(data) > maxProperties:
            raise ValidationError('{0} 属性数量不能大于{1}'.format(title, str(maxProperties)))
        if minProperties and len(data) < minProperties:
            raise ValidationError('{0} 属性数量不能小于{1}'.format(title, str(minProperties)))
        if required:
            miss = [i for i in required if i not in data.keys()]
            if miss:
                raise ValidationError('必须包含属性{0}'.format(','.join(miss)))

        for key, value in data.items():
            if strict and key not in properties.keys():
                raise ValidationError('{0}不在预期的属性列表中'.format(str(key)))
            if not strict and key not in properties.keys():
                continue
            data_validate(properties[key], value, top=False, name=key)
        return

    elif rtype == 'array':
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
            raise ValidationError('{0} 元素数量不能大于{1}'.format(title, str(maxItems)))
        if minItems and len(data) < minItems:
            raise ValidationError('{0} 元素数量不能小于{1}'.format(title, str(minItems)))
        if uniqueItems:
            used = []
            unique = [used.append(x) for x in data if x not in used]
            if len(unique) != len(data):
                raise ValidationError('{0} 元素必须唯一'.format(title))
        if not items:
            return
        for i in data:
            data_validate(items, i, top=False)

        return

    elif top:
        raise SchemaError('无效的数据模型:{0}'.format('只能是列表或字典'))

    if enum and not isinstance(enum, list):
        raise SchemaError('无效的数据模型:{0}'.format('枚举值必须通过列表传入'))
    

    if rtype == 'string':
        if not isinstance(data, basestring):
            raise ValidationError('{0} 值必须是字符类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]))
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
                raise SchemaError('无效的数据模型:{0}'.format(''))
        if rformat and rformat not in ['email', 'ipv4', 'alpha', 'alnum', 'date', 'datetime', 'price', 'json']:
            raise SchemaError('无效的数据模型:{0}'.format(''))


        if maxLength and len(data) > maxLength:
            raise ValidationError('{0} 值长度不能大于{1}'.format(title, str(maxLength)))
        if minLength and len(data) < minLength:
            raise ValidationError('{0} 值长度不能小于{1}'.format(title, str(minLength)))
        if pattern and  not re.match(rule, data):
            raise ValidationError('{0} 值不合理'.format(title))

        if not rformat:
            return

        if rformat == 'alpha' and not data.isalpha():
            raise ValidationError('{0} 值要求只包含英文字母'.format(title))
        if rformat == 'alnum' and not data.isalnum():
            raise ValidationError('{0} 值要求只包含数字'.format(title))
        if rformat == 'email' and not re.match('[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$'):
            raise ValidationError('{0} 值要求邮箱格式'.format(title))
        if rformat == 'ipv4' and not re.match('^((0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])\.){3}(0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])$'):
            raise ValidationError('{0} 值要求IPv4格式'.format(title))
        if rformat == 'price' and not re.match('^[0-9]{1,8}(\.[0-9]{1,2}){0,1}$'):
            raise ValidationError('{0} 值要求只包含数字和小数点'.format(title))
        if rformat == 'date':
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d')
            except ValueError:
                raise ValidationError('{0} 值要求日期格式:YYYY-mm-dd'.format(title))
        if rformat == 'datetime':
            try:
                datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValidationError('{0} 值要求日期+时间格式:YYYY-mm-dd HH:MM:S'.format(title))
        if rformat == 'json':
            try:
                json.loads(data)
            except ValueError:
                raise ValidationError('{0} 值要求json格式'.format(title))

        return

    if rtype == 'boolean':
        if not isinstance(data, bool):
            raise ValidationError('{0} 值必须是布尔类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]))
        return 

    if rtype in ['integer', 'number']:
        if rtype == 'integer' and not isinstance(data, (int, long)):
            raise ValidationError('{0} 值必须是整数, 您输入的是{1}'.format(title, str(type(data))[6:-1]))

        if rtype == 'number' and not isinstance(data, (int, long, float, complex)):
            raise ValidationError('{0} 值必须是数字, 您输入的是{1}'.format(title, str(type(data))[6:-1]))

        maximum = schema.get('maximum')
        minimum = schema.get('minimum')
        if maximum and not isinstance(maximum, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('maximum必须是数字'))
        if minimum and not isinstance(minimum, (int, long)):
            raise SchemaError('无效的数据模型:{0}'.format('minimum必须是数字'))
        if maximum and len(data) > maximum:
            raise ValidationError('{0} 值不能大于{1}'.format(title, str(maximum)))
        if minimum and len(data) < minimum:
            raise ValidationError('{0} 值不能小于{1}'.format(title, str(minimum)))

        return


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
            'default': {'type': 'interge'},
            'order': {'type': 'interge'},
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