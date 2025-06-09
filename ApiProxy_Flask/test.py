import xmlrpc.client

# Create a connection to the Odoo server
server = xmlrpc.client.ServerProxy('http://odoo-host/web/service/bus')

# Define the parameters for creating an account
params = {
    'name': 'John Doe',
    'type': 'res.partner'
}

# Call the "create" method of the Odoo server using XmlRPC
account_id = server.execute('create', params)

# Define the parameters for updating an account
update_params = {
    'id': account_id,
    'name': 'Jane Smith'
}

# Call the "write" method of the Odoo server using XmlRPC
server.execute('write', update_params)

# Define the parameters for deleting an account
delete_params = {
    'id': account_id
}

# Call the "unlink" method of the Odoo server using XmlRPC
server.execute('unlink', delete_params)
```### Instruction:
 Write a Python program to create a user in an Odoo instance, update it and delete it using the `xmlrpc` library.
