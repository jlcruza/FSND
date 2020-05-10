export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'my-fsnd-coffee-shop', // the auth0 domain prefix
    audience: 'coffee-identifier', // the audience set for the auth0 app
    clientId: 'WnKs5CL02wTyyH0ZBfpFyaFNxeJKo9JX', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
