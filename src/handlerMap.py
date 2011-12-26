#{%block imports%}
from controllers import BaseControllers
from controllers import ShellControllers
from controllers import HalWebControllers
from controllers import cmsControllers
#{%endblock%}
webapphandlers = [
#{%block ApplicationControllers %}


#{%block BaseControllers %}
('/Login', BaseControllers.LoginController),
('/Login/(.*)', BaseControllers.LoginController),
('/Logout',BaseControllers.LogoutController),
('/AddUser', BaseControllers.AddUserController),
('/WishList', BaseControllers.WishListController),
('/admin/Role', BaseControllers.RoleController),
('/admin/RoleAssociation', BaseControllers.RoleAssociationController),
('/Base/WishList', BaseControllers.WishListController),
('/Base/Invitation', BaseControllers.InvitationController),
#{%endblock%}

#{%block ShellControllers%}
('/admin/Shell', ShellControllers.FrontPageController),
('/admin/stat.do', ShellControllers.StatementController),
#{%endblock%}

#{%block cmsControllers}
#for diplaying contents created by a user.
('/cms/contents', cmsControllers.CMSContentController.new_factory(op='my_contents')),
#for diplaying specifyc content by it's key
('/cms/content/(.*)', cmsControllers.CMSContentController),
#links page
('/cms/links', cmsControllers.CMSLinksController),

#comments for a specific page (add, edit and display(Not used now)
('/cms/page/(.*)/comment', cmsControllers.CommentController.new_factory(op='edit')),
('/cms/page/(.*)/comments', cmsControllers.CommentController.new_factory(op='index')),

#display a link
('/cms/page/(.*)', cmsControllers.CMSPageController.new_factory(op='view')),
#display pages by tag
('/cms/tag/(.*)', cmsControllers.CMSPageController.new_factory(op='index')),
#display latest pages
('/', cmsControllers.CMSPageController.new_factory(op='index')),
#menus controllers , singlemenu by name
('/menu/(.*)', cmsControllers.MenuController.new_factory(op='view')),
('/menu', cmsControllers.MenuController),
#{%endblock%}

#{%block HalWebControllers%}
('/', HalWebControllers.WelcomeController),
#{%endblock%}

#{%endblock%}
]

