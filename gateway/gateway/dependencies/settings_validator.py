from dynaconf import settings, Validator


settings.validators.register(
    Validator("OPENEO_VERSION", must_exist=True),

    # RabbitMQ
    Validator("RABBIT_USER", must_exist=True),
    Validator("RABBIT_PASSWORD", must_exist=True),
    Validator("RABBIT_HOST", must_exist=True),
    Validator("RABBIT_PORT", must_exist=True, is_type_of=int),

    # OIDC
    Validator("SECRET_KEY", must_exist=True),

    # User DB
    Validator("DB_USER", must_exist=True),
    Validator("DB_PASSWORD", must_exist=True),
    Validator("DB_HOST", must_exist=True),
    Validator("DB_PORT", must_exist=True, is_type_of=int),
    Validator("DB_NAME", must_exist=True),

    # File Upload
    Validator("UPLOAD_TMP_DIR", must_exist=True),
)
