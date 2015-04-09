# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    auth.settings.login_next=URL('home')
    return dict(form=auth())




@auth.requires_login()
def home():
 
    logname = auth.user.first_name
    logid = int(auth.user.id)   
    k=-1
    if len(request.args)==0 or len(request.args)>1:
        redirect(URL('home',args=(logid)))

    elif len(request.args) == 1:
        name = request.args[0]
        for row in db().select(db.auth_user.ALL):
            if int(row.id) == int(name):
                k = row.first_name

    flist=[]
    frlist=[]

    for row in db().select(db.freq.ALL):
        if int(row.friend_id1) == logid:
            flist.append(int(row.friend_id2))

    for row in db().select(db.friend.ALL):
        id1 = int(row.friend_id1)
        id2 = int(row.friend_id2)

        if id1 == logid:
            frlist.append(id2)
        elif id2 == logid:
            frlist.append(id1)

    import os
    form = SQLFORM.factory(Field('description','string'),
            Field('image', 'upload', requires=IS_IMAGE(),uploadfolder=os.path.join(request.folder,'uploads') ) 
            )
    if form.process().accepted:
        stream = open(request.folder+'uploads/'+form.vars.image, 'rb')
        db.post.insert(person_id=logid,description=form.vars.description,image=stream)
        response.flash = 'form accepted'
    elif form.errors:
        print "you asshole"

    post=[]
    for row in db().select(db.post.ALL):
        pid=row.person_id
        des=row.description
        img=row.image
        post.append((pid,des,img))

    return dict(data="Welcome %(first_name)s" % auth.user, name=k , flist=flist , frlist=frlist,form = form, post=post)




def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
