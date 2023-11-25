from .entities.User import User


class ModelUser():

    @classmethod
    def login(self, db, user):
        try:
            sql = """SELECT usuarioid, usuario, contrasena, nombre, rolid FROM usuario 
                    WHERE usuario = '{}'""".format(user.username)
            db.execute(sql)
            row = db.fetchone()

            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3], row[4])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            sql = "SELECT usuarioid, usuario, contrasena, nombre, rolid FROM usuario WHERE usuarioid = {}".format(id)
            db.execute(sql)
            row = db.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[3], row[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def update(self, db, id, nombre, contrasena):
        try:
            contrasenaHash= User.generate_password(contrasena)
            sql = "UPDATE usuario SET nombre='{}', contrasena='{}' WHERE usuarioid = {}".format(nombre, contrasenaHash, id)
            db.execute(sql)
            return True

        except Exception as ex:
            raise Exception(ex)