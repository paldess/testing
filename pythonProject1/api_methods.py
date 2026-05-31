from flask import request, jsonify
from connects import connect_read, connect_write



def api_user():
    key = request.args.get('api_key_user')
    try:
        api_key_data = connect_read(f'select email from users where api_token = "{key}";')[0]
    except:
        return jsonify({'Error': 'access denied'})
    # Чтение
    if request.args.get('update') == 'False':
        if len(api_key_data) == 1:
            data_user = connect_read(f'select email, activ_group, is_active from users where email = "{request.args.get('email')}";', True)[0]
            data_page_access = [i[0] for i in connect_read(f'select adress from pages '
                                                           f'join permissions p on p.page = pages.id '
                                                           f'where p.group_access = {data_user["activ_group"]};')]
            data_user['access'] = data_page_access
        else:
            data_user = {'Error': 'There is more than one user with this name'}
        return jsonify(data_user)
    # Обновление
    else:
        if len(api_key_data) == 1:
            connect_write(f'delete from permissions where group_access = {request.args.get("group")};')
            for i in request.args.get('group_access').split(','):
                sql_add_access = f'insert into permissions(page, group_access) values({i}, {request.args.get("group")});'
                result = connect_write(sql_add_access)
            # data_user = connect_write(f'update permissions set group_access="{request.args.get('group_access')}" '
            #                           f'where email = "{request.args.get('email')}";')
            if result == True:
                return jsonify({'Result': 'Successfully updated'})
            else:
                return jsonify({'Error': 'Unknown cause'})
        else:
            return jsonify({'Error': 'There is more than one user with this name'})

