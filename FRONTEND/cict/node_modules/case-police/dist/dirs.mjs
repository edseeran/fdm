import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const distDir = fileURLToPath(new URL("../dist", import.meta.url));
const dictDir = resolve(distDir, "../dict");

export { dictDir, distDir };
