from lib.routes.route import Route
webapphandlers=(
      Route('home', '/', controller="cmslinks", action="index", menu='pages'),
      Route('login', '/login', controller="login", action="login"),
      Route('logout', '/logout', controller="login", action="logout"),
      Route('default', '{controller}/{action}'),
      Route('default_id', '{controller}/{action}/{id}')
)
