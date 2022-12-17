ALTER TABLE public.usuario ADD rolid int4 NULL;

CREATE TABLE public.rol (
	rolid int4 NULL,
	nombre varchar NULL
);

INSERT INTO public.rol (rolid,nombre) VALUES 
(1,'administrador')
,(2,'vendedor')
;

-- Actual parameter values may differ, what you see is a default string representation of values
UPDATE public.usuario
SET contrasena='pbkdf2:sha256:260000$fL4PTZI97PfLIuYU$2bf0f91a8438e4a496e582556fa9901373048375165d8011ea0af41af4039ed0'
WHERE usuarioid=1;
UPDATE public.usuario
SET contrasena='pbkdf2:sha256:260000$JsotyPW9x1xph4Ez$85799e2b12beb06ac78e0dd0cb86887040a0f22a613450082f9141a68b6d6d77'
WHERE usuarioid=3;
UPDATE public.usuario
SET contrasena='pbkdf2:sha256:260000$yXObQzZF5REEoYLO$29d37347e8d92e31c0e6041aea7692b9be5a03646b0efdfb3e055f5ce2495c47'
WHERE usuarioid=2;

-- Actual parameter values may differ, what you see is a default string representation of values
INSERT INTO public.usuario (usuarioid,nombre,contrasena)
VALUES (4,'venta','pbkdf2:sha256:260000$9Vz1tKvI3fWtD1Ca$916cbd7d233fe01f28f17172c876b96fd0e0826978a6b5e1f417a52ac8134992');

-- Actual parameter values may differ, what you see is a default string representation of values
UPDATE public.usuario
SET rolid=1
WHERE usuarioid=1;
UPDATE public.usuario
SET rolid=1
WHERE usuarioid=3;
UPDATE public.usuario
SET rolid=1
WHERE usuarioid=2;
UPDATE public.usuario
SET rolid=2
WHERE usuarioid=4;


ALTER TABLE public.operaciones ADD usuarioid int4 NULL;
ALTER TABLE public.caja ADD usuarioid int4 NULL;


-- Actual parameter values may differ, what you see is a default string representation of values
INSERT INTO public.banco (bancoid,nombre,orden)
VALUES (18,'EFECTIVO (Caja Secundaria) - DOLARES',131);
INSERT INTO public.banco (bancoid,nombre,orden)
VALUES (19,'EFECTIVO (Caja Secundaria) - SOLES',121);
UPDATE public.banco
SET nombre='EFECTIVO (Caja Principal) - DOLARES'
WHERE bancoid=16;
UPDATE public.banco
SET nombre='EFECTIVO (Caja Principal) - SOLES'
WHERE bancoid=7;

