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


class GpySchema(object):

    def __init__(self, schema, ref=None):
        self.schema = schema
        self.ref = ref or {}
        self.checked = []

    def check_schema(self, schema=None, top=True):
        schema = schema or self.schema
        ref = self.ref
        if not isinstance(schema, dict) or not schema:
            raise SchemaError('无效的数据模型:{0}, 您输入的是{1}'.format('schema必须是非空字典', schema))

        rtype = schema.get('type')
        enum = schema.get('enum')
        rnot = schema.get('not')
        anyOf = schema.get('anyOf')
        message = schema.get('message')
        _ref = schema.get('$ref')
        if not rtype and not _ref and not anyOf:
            raise SchemaError('无效的数据模型:{0}'.format('必须指定类型或$ref'))

        if rtype and rtype not in ['boolean', 'null', 'integer', 'number', 'string' ,'array', 'object']:
            raise SchemaError('无效的数据模型:{0} {1}'.format('无效的类型', rtype))

        if _ref:
            if not isinstance(_ref, basestring):
                raise SchemaError('无效的数据模型:{0}'.format('$ref要求是字符'))
            if not ref.get(_ref):
                raise SchemaError('无效的数据模型:{0}'.format('找不到$ref指定的schema'))

            if cmp(ref[_ref], schema) and _ref not in self.checked:
                self.checked.append(_ref)
                self.check_schema(ref.get(_ref), top=False)

        if message:
            if not isinstance(message, basestring):
                raise SchemaError('无效的数据模型:{0}'.format('自定义消息必须是有效的文本'))


        if enum and not isinstance(enum, list):
            raise SchemaError('无效的数据模型:{0}'.format('枚举值必须通过列表传入'))

        if rnot and not isinstance(rnot, dict):
            raise SchemaError('无效的数据模型:{0}'.format('not只能是字典'))
        if rnot:
            self.check_schema(rnot, top=False)

        if anyOf and not isinstance(anyOf, list):
            raise SchemaError('无效的数据模型:{0}'.format('anyOf只能是列表'))
        if anyOf:
            for rschema in anyOf:
                self.check_schema(rschema, top=False)

        if rtype == 'object':
            properties = schema.get('properties')
            if properties:
                for key, value in properties.items():
                    if not key or not isinstance(key, basestring):
                        raise SchemaError('无效的数据模型:{0}'.format('properties名称必须是字符'))
                    self.check_schema(value)
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
            if additionalProperties:
                self.check_schema(additionalProperties, top=False)
            if patternProperties and not isinstance(patternProperties, dict):
                raise SchemaError('无效的数据模型:{0}'.format('patternProperties必须是字典'))
            if patternProperties:
                for pattern, value in patternProperties.items():
                    if not isinstance(pattern, basestring):
                        raise SchemaError('无效的数据模型:{0}'.format('无法识别正则式'))
                    try:
                        rule = re.compile(pattern)
                    except:
                        raise SchemaError('无效的数据模型:{0}'.format('无法识别属性模式的正则式'))
                    self.check_schema(value, top=False)

        elif rtype == 'array':
            items = schema.get('items')
            if items:
                if isinstance(items, dict):
                    self.check_schema(items, top=False)
                elif isinstance(items, list):
                    for item in items:
                        self.check_schema(item, top=False)
                else:
                    raise SchemaError('无效的数据模型:{0}'.format('items类型无效'))
            maxItems = schema.get('maxItems')
            minItems = schema.get('minItems')
            uniqueItems = schema.get('uniqueItems')
            additionalItems = schema.get('additionalItems')
            if maxItems and not isinstance(maxItems, (int, long)):
                raise SchemaError('无效的数据模型:{0}'.format('maxItems必须是数字'))
            if minItems and not isinstance(minItems, (int, long)):
                raise SchemaError('无效的数据模型:{0}'.format('minItems必须是数字'))
            if uniqueItems and not isinstance(uniqueItems, bool):
                raise SchemaError('无效的数据模型:{0}'.format('uniqueItems必须是布尔值'))
            if additionalItems:
                self.check_schema(additionalItems, top=False)

        if rtype == 'string':
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

        if rtype in ['integer', 'number']:
            maximum = schema.get('maximum')
            minimum = schema.get('minimum')
            if maximum and not isinstance(maximum, (int, long)):
                raise SchemaError('无效的数据模型:{0}'.format('maximum必须是数字'))
            if minimum and not isinstance(minimum, (int, long)):
                raise SchemaError('无效的数据模型:{0}'.format('minimum必须是数字'))

    def validate(self, schema=None, data=None, name='', strict=True):
        schema = schema or self.schema

        rtype = schema.get('type')
        title = schema.get('title') or name or ''
        enum = schema.get('enum')
        rnot = schema.get('not')
        anyOf = schema.get('anyOf')
        message = schema.get('message')
        _ref = schema.get('$ref')
        if message:
            message = message.format(name = title, value = data, title = title, data = data)

        if enum and data not in enum:
            raise ValidationError(message or '{0} 值必须在指定区域内, 该区域是({1})'.format(title, ','.join(str(i) for i in enum)), 'enum', title)

        if rnot:
            try:
                correct = self.validate(rnot, data, name=title, strict=strict)
            except ValidationError:
                correct = None
            if correct:
                raise ValidationError(message or '{0} 值 {1} 不被允许'.format(title, str(data)), 'not', title)

        if anyOf:
            correct = None
            for rschema in anyOf:
                if correct is not None:
                    continue
                try:
                    self.validate(rschema, data, name=title, strict=strict)
                    correct = True
                except ValidationError:
                    correct = None
            if correct is None:
                raise ValidationError(message or '{0} 值 {1} 不合理或格式错误'.format(title, data), 'anyOf', title)
            return True

        if _ref:
            rschema = self.ref.get(_ref)
            self.validate(rschema, data, name=title, strict=strict)


        if rtype == 'object':
            if not isinstance(data, dict):
                raise ValidationError(message or '{0} 值必须是字典, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)

            properties = schema.get('properties', {})
            maxProperties = schema.get('maxProperties')
            minProperties = schema.get('minProperties')
            dependencies = schema.get('dependencies')
            patternProperties = schema.get('patternProperties')
            additionalProperties = schema.get('additionalProperties')
            required = schema.get('required')

            if maxProperties and len(data) > maxProperties:
                raise ValidationError(message or '{0} 属性数量不能大于{1}'.format(title, str(maxProperties)), 'maxProperties', title)
            if minProperties and len(data) < minProperties:
                raise ValidationError(message or '{0} 属性数量不能小于{1}'.format(title, str(minProperties)), 'minProperties', title)
            if required:
                miss = [i for i in required if i not in data.keys()]
                if miss:
                    raise ValidationError(message or '{0}必须包含属性{1}'.format(title, ','.join(miss)), 'required', title)

            patternList = patternProperties.keys() if patternProperties else []
            for key, value in properties.items():
                if key in data.keys():
                    self.validate(value, data[key], name=key, strict=strict)

            for key, value in data.items():
                if key in properties.keys():
                    continue
                if patternList:
                    matchList = [p for p in patternList if re.match(p, key)]
                    for p in matchList:
                        self.validate(patternProperties[p], value, name=key, strict=strict)
                    if matchList:
                        continue
                if additionalProperties:
                    self.validate(additionalProperties, value, name=key, strict=strict)
                    continue
                if additionalProperties is False:
                    raise ValidationError(message or '{0}不是有效的属性名'.format(str(key)), 'additionalProperties', title)
            return True

        elif rtype == 'array':
            if strict:
                if not isinstance(data, list):
                    raise ValidationError(message or '{0} 值必须是列表, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)
            else:
                if not isinstance(data, (list, tuple)):
                    raise ValidationError(message or '{0} 值必须是列表或元组, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)

            items = schema.get('items')
            maxItems = schema.get('maxItems')
            minItems = schema.get('minItems')
            uniqueItems = schema.get('uniqueItems')
            additionalItems = schema.get('additionalItems')
            if isinstance(maxItems, int) and len(data) > maxItems:
                raise ValidationError(message or '{0} 元素数量不能大于{1}'.format(title, str(maxItems)), 'maxItems', title)
            if isinstance(minItems, int) and len(data) < minItems:
                raise ValidationError(message or '{0} 元素数量不能小于{1}'.format(title, str(minItems)), 'minItems', title)
            if uniqueItems:
                used = []
                unique = [used.append(x) for x in data if x not in used]
                if len(unique) != len(data):
                    raise ValidationError(message or '{0} 元素必须唯一'.format(title), 'uniqueItems', title)


            if isinstance(items, dict):
                for i in data:
                    self.validate(items, i, name=title, strict=strict)
            elif isinstance(items, list):
                item_len = len(items)
                if additionalItems is False:
                    if len(data) > item_len:
                        raise ValidationError(message or '{0} 元素数量超过规定值'.format(title), 'additionalItems', title)
                elif additionalItems:
                    for i in data[item_len:]:
                        self.validate(additionalItems, i, name=title, strict=strict)
                for index, i in enumerate(data[:item_len]):
                    self.validate(items[index], i, name=title, strict=strict)
            else:
                item_len = 0
                if additionalItems is False:
                    if len(data) > item_len:
                        raise ValidationError(message or '{0} 元素数量超过规定值'.format(title), 'additionalItems', title)
                elif additionalItems:
                    for i in data[item_len:]:
                        self.validate(additionalItems, i, name=title, strict=strict)

            return True

        if rtype == 'string':
            if not isinstance(data, basestring):
                raise ValidationError(message or '{0} 值必须是字符类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)
            maxLength = schema.get('maxLength')
            minLength = schema.get('minLength')
            pattern = schema.get('pattern')
            rformat = schema.get('format')

            if isinstance(maxLength, int) and len((unicode(str(data),"utf-8"))) > maxLength:
                raise ValidationError(message or '{0} 值长度不能大于{1}'.format(title, str(maxLength)), 'maxLength', title)
            if isinstance(minLength, int) and len((unicode(str(data),"utf-8"))) < minLength:
                raise ValidationError(message or '{0} 值长度不能小于{1}'.format(title, str(minLength)), 'minLength', title)
            if pattern and  not re.match(rule, data):
                raise ValidationError(message or '{0} 值不合理'.format(title), 'pattern', title)

            if not rformat:
                return True

            if rformat == 'alpha' and not data.isalpha():
                raise ValidationError(message or '{0} 值要求只包含英文字母'.format(title), 'format', title)
            if rformat == 'alnum' and not data.isalnum():
                raise ValidationError(message or '{0} 值要求只包含数字'.format(title), 'format', title)
            if rformat == 'email' and not re.match('[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$', data):
                raise ValidationError(message or '{0} 值要求邮箱格式'.format(title), 'format', title)
            if rformat == 'ipv4' and not re.match('^((0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])\.){3}(0|[1-9]\d?|[0-1]\d{2}|2[0-4]\d|25[0-5])$', data):
                raise ValidationError(message or '{0} 值要求IPv4格式'.format(title), 'format', title)
            if rformat == 'price' and not re.match('^[0-9]{1,8}(\.[0-9]{1,2}){0,1}$', data):
                raise ValidationError(message or '{0} 值要求只包含数字和小数点'.format(title), 'format', title)
            if rformat == 'date':
                try:
                    datetime.datetime.strptime(data, '%Y-%m-%d')
                except ValueError:
                    raise ValidationError(message or '{0} 值要求日期格式:YYYY-mm-dd'.format(title), 'format', title)
            if rformat == 'datetime':
                try:
                    datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValidationError(message or '{0} 值要求日期+时间格式:YYYY-mm-dd HH:MM:SS'.format(title), 'format', title)
            if rformat == 'json':
                try:
                    json.loads(data)
                except ValueError:
                    raise ValidationError('{0} 值要求json格式'.format(title), 'format', title)
            if rformat == 'regex':
                try:
                    re.compile(data)
                except:
                    raise ValidationError('{0} 值不是有效的正则式'.format(title), 'format', title)

            return True

        if rtype == 'boolean':
            if strict:
                if not isinstance(data, bool):
                    raise ValidationError(message or '{0} 值必须是布尔类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)
            else:
                if data not in [True, False, 0, 1]:
                    raise ValidationError(message or '{0} 值必须是布尔类型, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)

            return True

        if rtype in ['integer', 'number']:
            if strict:
                if rtype == 'integer' and not isinstance(data, (int, long)):
                    raise ValidationError(message or '{0} 值必须是整数, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)

                if rtype == 'number' and not isinstance(data, (int, long, float, complex)):
                    raise ValidationError(message or '{0} 值必须是数字, 您输入的是{1}'.format(title, str(type(data))[6:-1]), 'type', title)
            else:
                if rtype == 'integer' and not (isinstance(data, (int, long)) or (isinstance(data, basestring) and data.isdigit())):
                    raise ValidationError(message or '{0} 值必须是整数或整数字符, 您输入的是 {1}'.format(title, data, 'type', title))

                if rtype == 'number':
                    try:
                        float(data)
                    except ValueError:
                        raise ValidationError(message or '{0} 值必须是数字或数字字符, 您输入的是 {1}'.format(title, data), 'type', title)

            maximum = schema.get('maximum')
            minimum = schema.get('minimum')
            if isinstance(maximum, int) and data > maximum:
                raise ValidationError(message or '{0} 值不能大于{1}'.format(title, str(maximum)), 'maximum', title)
            if isinstance(minimum, int) and data < minimum:
                raise ValidationError(message or '{0} 值不能小于{1}'.format(title, str(minimum)), 'minimum', title)

            return True

        if rtype == 'null':
            if strict:
                if data is not None:
                    raise ValidationError(message or '{0} 值必须是None, 您输入的是 {1}'.format(title, str(type(data))[6:-1]), 'type', title)
            else:
                if data is not None and data != '':
                    raise ValidationError(message or '{0} 值必须是空值, 您输入的是 {1}'.format(title, data), 'type', title)

            return True


class DataValidationError(Exception):

    def __init__(self, value):
        Exception.__init__(self, value)


class DataValidation(object):

    def __init__(self):
        self.schema_dict = {}

    def validate(self, schema, data, ref=None, strict=True):
        validator = self.__get_validator(schema, ref=ref)
        try:
            validator.validate(data=data, strict=strict)
        except ValidationError as e:
            raise DataValidationError(e.message)


    def form_data(self, schema, data):
        validator = self.__get_validator(schema, ref=None, top=False)
        new = {}
        cache = {}
        for key, value in schema['properties'].items():
            title = value.get('title') or key
            if key not in data.keys():
                cache[key] = None
                continue
            if value['type'] == 'array':
                if len(data[key]) < 1:
                    new[key] = []
                    continue
                items = value.get('items')
                if items and items.get('type') == 'number':
                    try:
                        new[key] = [int(i) for i in data[key]]
                        continue
                    except:
                        raise DataValidationError('不合理的值 {0},  {1}必须是数字'.format(','.join(data[key]), title))
                new[key] = data[key]
            elif value['type'] in ['string', 'number']:
                if len(data[key]) < 1:
                    new[key] = None
                    continue
                if value['type'] == 'number':
                    if len(data[key][0]) < 1:
                        cache[key] = None
                        continue
                    try:
                        new[key] = int(data[key][0])
                        continue
                    except:
                        raise DataValidationError('不合理的值 {0}, {1}必须是数字'.format(','.join(data[key]), title))
                new[key] = data[key][0]
            elif value['type'] == 'object':
                if len(data[key]) < 1:
                    new[key] = None
                    continue
                try:
                    new[key] = json.loads(data[key][0])
                except:
                    raise DataValidationError('{0} 字段格式错误'.format(title))
        self.validate(schema, new)
        new.update(cache)
        return new


    def __get_validator(self, schema, ref, top=True):
        schema_text = str(schema)
        if self.schema_dict.get(schema_text) is False:
            raise DataValidationError('系统配置错误, 请联系管理员')
        elif self.schema_dict.get(schema_text) is None:
            validator = GpySchema(schema, ref)
            try:
                validator.check_schema(top=top)
                # log.debug('gen validator and check pass. schema is {0}'.format(schema_text))
            except SchemaError as e:
                # log.error('schema check failed, error message is {0}. Schema is {1}'.format(e.message, schema))
                self.schema_dict[schema_text] = False
                raise DataValidationError('系统配置错误, 请联系管理员')
            self.schema_dict[schema_text] = validator
        else:
            validator = self.schema_dict.get(schema_text)
        return validator

dv = DataValidation()
