    #! /usr/bin/env python
#-*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****

#
#
# ***** END LICENSE BLOCK *****

__author__ = ""
__version__ = ""
__date__ = ""
__revision__ = ""
__copyright__ = ""
__license__ = ""

#from bootstrap import db
from bootstrap import db
from sqlalchemy.sql import func, select
from flask import Blueprint, jsonify, request
from collections import defaultdict
from web.models import Shelter, Attribute, Property, Value, Association, ShelterPicture, Category

api_bp = Blueprint('api for shelter', __name__, url_prefix='/api/v0.1')

def tree():
    return defaultdict(tree)

def queryfactory(model,join=False,filt=False,value=False):
	
	#helper functions to construct queries
	def filter_or(obj,attrib,val):
		"""Construct filtering method (OR)"""
		list(val)
		if len(val) == 1:
			return obj.filter(attrib == val[0])
		else: 
			return obj.filter(attrib.in_(val))
	
	def filter_and(obj,attrib,val):
		"""Construct filtering methods recursively (AND)"""
		list(val)
		if len(val) == 1:
			return obj.filter(attrib == val[0])
		else: 
			return filter_and(obj.filter(attrib == val[len(val)-1]),attrib, val[0:len(val)-1])

	if join and not filt:
		return model.query.join(join)
	elif filt and join:
		return filter_or(model.query.join(join),filt,value)
	elif filt and not join:
		return filter_or(model.in_(value))
	else:
		return "error"

@api_bp.route('/', methods=['GET'])
def apimessage():
    message = tree()
    message["API version"] = 0.1
    message["Message"] = "This is the development API"
    return jsonify(message)

@api_bp.route('/attributes/<attribute_name>', methods=['GET'])
def getattributes(attribute_name, safetext=False):
    """Returns available values for a given attribute name, separated by semicolons"""
    result= tree()
    
    attributes = Attribute.query.filter(Attribute.uniqueid==attribute_name).\
                                first().associated_values
   
    result[attribute_name] = ";".join([attribute.name for attribute in attributes])
    return jsonify(result)

@api_bp.route('/shelters', methods=['GET'])
#@api_bp.route('/shelters/<int:shelter_id>', methods=['GET'])
def allshelters():
    """Returns all shelters and their properties"""
    result = tree()
    
    #shelter pictures folder path
    picpath = 'data/shelters/pictures'
    
    querybase = db.session.query(Property.shelter_id,Attribute.name,Attribute.uniqueid,func.string_agg(Value.name,';').label("value"))\
    		.join(Attribute)\
    		.join(Association,Property.id==Association.property_id)\
    		.join(Value, Association.value_id==Value.id)\
    		.group_by(Property.shelter_id, Attribute.name, Attribute.uniqueid)
    
    picquerybase = db.session.query(ShelterPicture.shelter_id, ShelterPicture.file_name.label("filename"), Category.name)\
    		.join(Category, Category.id == ShelterPicture.category_id)		
    
    ##queries if no request arguments
    shelter_properties = querybase
    shelter_pictures = picquerybase
    
    if request.args.getlist('attribute'):
    	attribute = request.args.getlist('attribute')	
    	
    	subquery = db.session.query(Property.shelter_id)\
    			.join(Attribute, Attribute.id==Property.attribute_id)\
    			.filter(Attribute.uniqueid.in_(attribute))\
    			.group_by(Property.shelter_id)
    			
    	shelter_properties = querybase.filter(subquery.subquery().c.shelter_id==Property.shelter_id)
    	shelter_pictures = picquerybase.filter(subquery.subquery().c.shelter_id==ShelterPicture.shelter_id)

    if request.args.getlist('value'):
    	value = request.args.getlist('value')
    	if not request.args.getlist('attribute'):
    		subquery = db.session.query(Property.shelter_id)\
    			.join(Attribute, Attribute.id==Property.attribute_id)\
    			.filter(Property.values.any(Value.name.in_(value)))\
    			.group_by(Property.shelter_id)
    	else:
    		subquery = subquery.filter(Property.values.any(Value.name.in_(value)))
    	
    	shelter_properties = querybase.filter(subquery.subquery().c.shelter_id==Property.shelter_id)
    	shelter_pictures = picquerybase.filter(subquery.subquery().c.shelter_id==ShelterPicture.shelter_id)
    
    #print(shelter_properties)
    #print(shelter_pictures)
    
    if request.args.get('format') == 'prettytext':
    	for shelter_property in shelter_properties:
    		result[shelter_property.shelter_id][shelter_property.name] = shelter_property.value
    	
    	for picture in shelter_pictures:
    		if not result[picture.shelter_id]["shelterpicture"][picture.name]:
    			result[picture.shelter_id]["shelterpicture"][picture.name] = ["{}/{}/{}".format(picpath, result[picture.shelter_id]["ID"], picture.filename)]
    		else:
    			result[picture.shelter_id]["shelterpicture"][picture.name].append("{}/{}/{}".format(picpath, result[picture.shelter_id]["ID"], picture.filename))
    
    else:
    	for shelter_property in shelter_properties:
    		result[shelter_property.shelter_id][shelter_property.uniqueid] = shelter_property.value
    
    	for picture in shelter_pictures:
    		if not result[picture.shelter_id]["shelterpicture"][picture.name]:
    			result[picture.shelter_id]["shelterpicture"][picture.name] = ["{}/{}/{}".format(picpath, result[picture.shelter_id]["id"], picture.filename)]
    		else:
    			result[picture.shelter_id]["shelterpicture"][picture.name].append("{}/{}/{}".format(picpath, result[picture.shelter_id]["id"], picture.filename))
  
    return jsonify(result)


@api_bp.route('/shelters/<int:shelter_id>', methods=['GET'])
def shelters(shelter_id):
    """Returns specific shelter with its properties"""
    result = tree()
    
    ## shelter picture query
    shelter_pictures = db.session.query(ShelterPicture.shelter_id, func.string_agg(ShelterPicture.file_name,';').label("filename"), Category.name)\
    		.join(Category, Category.id == ShelterPicture.category_id)\
    		.group_by(ShelterPicture.shelter_id, Category.name)\
    		.filter(ShelterPicture.shelter_id==shelter_id)
    
    ## shelter property query
    shelter_properties  = Property.query.filter(Property.shelter_id==shelter_id)
    for shelter_property in shelter_properties:
    	result[shelter_property.shelter_id][shelter_property.attribute.uniqueid] = shelter_property.get_values_as_string()
    for picture in shelter_pictures:
    		result[picture.shelter_id]["shelterpicture"][picture.name] = picture.filename
    return jsonify(result)

@api_bp.route('/shelters/<attribute_name>', methods=['GET'])
@api_bp.route('/shelters/<attribute_name>/<attribute_value>', methods=['GET'])
def attributes(attribute_name, attribute_value=''):
    """Returns all shelters which match a specific attribute name or attribute name + value"""
    result = tree()
    if not attribute_value:
    	shelter_properties = Property.query.filter(Property.attribute.has(uniqueid=attribute_name))
    else:
    	shelter_properties = Property.query.filter(Property.attribute.has(uniqueid=attribute_name), Property.values.any(name=attribute_value))
    
    for shelter_property in shelter_properties:
    	result[shelter_property.shelter_id][shelter_property.attribute.uniqueid] = shelter_property.get_values_as_string()
   
    return jsonify(result)
    
@api_bp.route('/shelters/search/<searchstring>', methods=['GET'])
def fulltext(searchstring):
    searchstring = request.args.get('string')
    print(searchstring)
    result= tree()
    document = db.session.query(Property.shelter_id,func.to_tsvector(func.string_agg(Value.name,' ')).label("text"))\
    		.join(Attribute)\
    		.join(Association,Property.id==Association.property_id)\
    		.join(Value, Association.value_id==Value.id)\
    		.group_by(Property.shelter_id)\
    		.subquery()
    searchquery = db.session.query(document).filter(document.c.text.match(searchstring))
    #print(searchquery)
    for shelter_property in searchquery:
    	#print(shelter_property)
    	result[shelter_property.shelter_id] = 1#shelter_property.text
    return jsonify(result)
    
