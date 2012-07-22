<VirtualHost *:80>
ServerName example.com
DocumentRoot /usr/local/share/apache2/sites/example.com/current/htdocs

<Directory /usr/local/share/apache2/sites/example.com/current/htdocs>
    Options FollowSymLinks
    AllowOverride All
    Order allow,deny
    Allow from All
</Directory>

</VirtualHost>
