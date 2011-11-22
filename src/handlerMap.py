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
('/cms/contents', cmsControllers.CMSContentController.new_factory(op='my_contents')),
('/cms/content/(.*)', cmsControllers.CMSContentController),
('/cms/links', cmsControllers.CMSLinksController),
('/cms/page/(.*)/comment', cmsControllers.CommentController.new_factory(op='edit')),
('/cms/page/(.*)/comments', cmsControllers.CommentController.new_factory(op='index')),
('/cms/page/(.*)', cmsControllers.CMSPageController.new_factory(op='view')),
('/cms/tag/(.*)', cmsControllers.CMSPageController.new_factory(op='index')),
('/', cmsControllers.CMSPageController.new_factory(op='index')),
('/menu/(.*)', cmsControllers.MenuController),
('/menus', cmsControllers.MenuController.new_factory(op='index')),

#{%endblock%}

#{%block HalWebControllers%}
('/', HalWebControllers.WelcomeController),
#{%endblock%}

#{%endblock%}
]

