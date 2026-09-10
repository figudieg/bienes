// Genera src/environments/environment.ts a partir de frontend/.env.
// Corre automáticamente antes de "npm start" y "npm run build" (ver package.json).
// No editar environment.ts a mano: los cambios se pierden en el próximo build/serve.

const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });

const apiUrl = process.env.API_URL;
const production = (process.env.PRODUCTION || 'false').toLowerCase() === 'true';

if (!apiUrl) {
  console.error(
    'Error: falta API_URL en frontend/.env.\n' +
    'Copia frontend/.env.example a frontend/.env y completa el valor antes de continuar.'
  );
  process.exit(1);
}

const content = `// ARCHIVO GENERADO AUTOMÁTICAMENTE por scripts/set-env.js a partir de frontend/.env.
// No editar a mano — los cambios se sobrescriben en el próximo "npm start" o "npm run build".
export const environment = {
  production: ${production},
  apiUrl: '${apiUrl}'
};
`;

const targetPath = path.resolve(__dirname, '..', 'src', 'environments', 'environment.ts');
fs.writeFileSync(targetPath, content);
console.log(`[set-env] environment.ts generado con apiUrl=${apiUrl}`);
