-- 1. DEPARTAMENTOS
CREATE TABLE IF NOT EXISTS departamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(50) NOT NULL DEFAULT 'El Salvador'
);

-- 2. USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('propietario','operador','arrendatario','admin')),
    verificado BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 3. SESIONES
CREATE TABLE IF NOT EXISTS sesiones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    dispositivo VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    expira_en TIMESTAMP NOT NULL,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 4. DOCUMENTOS_VERIFICACION
CREATE TABLE IF NOT EXISTS documentos_verificacion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('dui','licencia','rtn','certificacion')),
    url_documento VARCHAR(500) NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente','aprobado','rechazado')),
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 5. MAQUINAS
CREATE TABLE IF NOT EXISTS maquinas (
    id SERIAL PRIMARY KEY,
    propietario_id INTEGER NOT NULL REFERENCES usuarios(id),
    departamento_id INTEGER REFERENCES departamentos(id),
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    precio_dia DECIMAL(10,2) NOT NULL,
    ubicacion VARCHAR(150),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    imagen_url VARCHAR(500),
    estado VARCHAR(20) DEFAULT 'disponible' CHECK (estado IN ('disponible','alquilada','mantenimiento')),
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 6. ESPECIFICACIONES
CREATE TABLE IF NOT EXISTS especificaciones (
    id SERIAL PRIMARY KEY,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
    clave VARCHAR(50) NOT NULL,
    valor VARCHAR(150) NOT NULL,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 7. DISPONIBILIDAD
CREATE TABLE IF NOT EXISTS disponibilidad (
    id SERIAL PRIMARY KEY,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    motivo VARCHAR(100),
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 8. FOTOS_MAQUINAS
CREATE TABLE IF NOT EXISTS fotos_maquinas (
    id SERIAL PRIMARY KEY,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
    url_cloudinary VARCHAR(500) NOT NULL,
    public_id VARCHAR(200) NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    orden INTEGER DEFAULT 0,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 9. OPERADORES
CREATE TABLE IF NOT EXISTS operadores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    experiencia_anios INTEGER DEFAULT 0,
    tarifa_dia DECIMAL(10,2),
    certificaciones TEXT,
    verificado BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 10. ALQUILERES
CREATE TABLE IF NOT EXISTS alquileres (
    id SERIAL PRIMARY KEY,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id),
    arrendatario_id INTEGER NOT NULL REFERENCES usuarios(id),
    operador_id INTEGER REFERENCES operadores(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    precio_acordado DECIMAL(10,2) NOT NULL,
    costo_total DECIMAL(10,2),
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente','activo','finalizado','cancelado')),
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 11. CALIFICACIONES
CREATE TABLE IF NOT EXISTS calificaciones (
    id SERIAL PRIMARY KEY,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    alquiler_id INTEGER NOT NULL REFERENCES alquileres(id),
    estrellas INTEGER NOT NULL CHECK (estrellas BETWEEN 1 AND 5),
    comentario TEXT,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- 12. FAVORITOS
CREATE TABLE IF NOT EXISTS favoritos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
    creado_en TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id, maquina_id)
);

-- 13. DISPOSITIVOS
CREATE TABLE IF NOT EXISTS dispositivos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fcm_token VARCHAR(500) NOT NULL,
    plataforma VARCHAR(20) DEFAULT 'android' CHECK (plataforma IN ('android','ios','web')),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Datos iniciales de departamentos de El Salvador
INSERT INTO departamentos (nombre, pais) VALUES
    ('San Salvador', 'El Salvador'),
    ('Santa Ana', 'El Salvador'),
    ('San Miguel', 'El Salvador'),
    ('La Libertad', 'El Salvador'),
    ('Sonsonate', 'El Salvador'),
    ('Usulután', 'El Salvador'),
    ('San Vicente', 'El Salvador'),
    ('Cuscatlán', 'El Salvador'),
    ('La Paz', 'El Salvador'),
    ('Chalatenango', 'El Salvador'),
    ('Morazán', 'El Salvador'),
    ('La Unión', 'El Salvador'),
    ('Cabañas', 'El Salvador'),
    ('Ahuachapán', 'El Salvador')
ON CONFLICT DO NOTHING;
