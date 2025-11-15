def register_routes(app):
    blueprints = {
        "api_routes": "/api",
        "auth_routes": "/api/auth",
        "admin_routes": "/api/admin",
        "doctor_routes": "/api/doctor",
        "paciente_routes": "/api/paciente",
        "main_routes": "/",
    }

    for module_name, prefix in blueprints.items():
        try:
            module = __import__(f"app.routes.{module_name}", fromlist=["*"])
            bp = getattr(module, f"{module_name.split('_')[0]}_bp")
            app.register_blueprint(bp, url_prefix=prefix)
            print(f"Registrado {module_name} en {prefix}")
        except Exception as e:
            print(f"Error registrando {module_name}: {e}")
