import type {PlatformIntegration} from 'sentry/types/project';

// If you update items of this list, please remember to update the "GETTING_STARTED_DOCS_PLATFORMS" list
// in the 'src/sentry/models/project.py' file. This way, they'll work together correctly.
// Otherwise, creating a project will cause an error in the backend, saying "Invalid platform".
export const platforms: PlatformIntegration[] = [
  {
    id: 'android',
    name: 'Android',
    type: 'framework',
    language: 'android',
    link: 'https://docs.sentry.io/platforms/android/',
  },
  {
    id: 'apple',
    name: 'Apple',
    type: 'language',
    language: 'apple',
    link: 'https://docs.sentry.io/platforms/apple/',
  },
  {
    id: 'apple-ios',
    name: 'iOS',
    type: 'language',
    language: 'apple',
    link: 'https://docs.sentry.io/platforms/apple/',
  },
  {
    id: 'apple-macos',
    name: 'macOS',
    type: 'language',
    language: 'apple',
    link: 'https://docs.sentry.io/platforms/apple/',
  },
  {
    id: 'bun',
    name: 'Bun',
    type: 'language',
    language: 'bun',
    link: 'https://docs.sentry.io/platforms/javascript/guides/bun/',
  },
  {
    id: 'capacitor',
    name: 'Capacitor',
    type: 'framework',
    language: 'capacitor',
    link: 'https://docs.sentry.io/platforms/javascript/guides/capacitor/',
  },
  {
    id: 'cordova',
    name: 'Cordova',
    type: 'language',
    language: 'cordova',
    link: 'https://docs.sentry.io/platforms/javascript/guides/cordova/',
  },
  {
    id: 'dart',
    name: 'Dart',
    type: 'framework',
    language: 'dart',
    link: 'https://docs.sentry.io/platforms/dart/',
  },
  {
    id: 'deno',
    name: 'Deno',
    type: 'language',
    language: 'deno',
    link: 'https://docs.sentry.io/platforms/javascript/guides/deno/',
  },
  {
    id: 'dotnet',
    name: '.NET',
    type: 'language',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/',
  },
  {
    id: 'dotnet-aspnet',
    name: 'ASP.NET',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/aspnet/',
  },
  {
    id: 'dotnet-aspnetcore',
    name: 'ASP.NET Core',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/aspnetcore/',
  },
  {
    id: 'dotnet-awslambda',
    name: 'AWS Lambda (.NET)',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/aws-lambda/',
  },
  {
    id: 'dotnet-gcpfunctions',
    name: 'Google Cloud Functions (.NET)',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/google-cloud-functions/',
  },
  {
    id: 'dotnet-maui',
    name: 'Multi-platform App UI (MAUI)',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/maui/',
  },
  {
    id: 'dotnet-uwp',
    name: 'UWP',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/uwp/',
  },
  {
    id: 'dotnet-winforms',
    name: 'Windows Forms',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/winforms/',
  },
  {
    id: 'dotnet-wpf',
    name: 'WPF',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/wpf/',
  },
  {
    id: 'dotnet-xamarin',
    name: 'Xamarin',
    type: 'framework',
    language: 'dotnet',
    link: 'https://docs.sentry.io/platforms/dotnet/guides/xamarin/',
  },
  {
    id: 'electron',
    name: 'Electron',
    type: 'language',
    language: 'electron',
    link: 'https://docs.sentry.io/platforms/javascript/guides/electron/',
  },
  {
    id: 'elixir',
    name: 'Elixir',
    type: 'language',
    language: 'elixir',
    link: 'https://docs.sentry.io/platforms/elixir/',
  },
  {
    id: 'flutter',
    name: 'Flutter',
    type: 'framework',
    language: 'flutter',
    link: 'https://docs.sentry.io/platforms/flutter/',
  },
  {
    id: 'go',
    link: 'https://docs.sentry.io/platforms/go/',
    name: 'Go',
    type: 'language',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/echo/',
    type: 'framework',
    id: 'go-echo',
    name: 'Echo',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/fasthttp/',
    type: 'framework',
    id: 'go-fasthttp',
    name: 'FastHTTP',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/fiber/',
    type: 'framework',
    id: 'go-fiber',
    name: 'Fiber',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/gin/',
    type: 'framework',
    id: 'go-gin',
    name: 'Gin',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/http/',
    type: 'framework',
    id: 'go-http',
    name: 'Net/Http',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/iris',
    type: 'framework',
    id: 'go-iris',
    name: 'Iris',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/martini/',
    type: 'framework',
    id: 'go-martini',
    name: 'Martini',
    language: 'go',
  },
  {
    link: 'https://docs.sentry.io/platforms/go/guides/negroni/',
    type: 'framework',
    id: 'go-negroni',
    name: 'Negroni',
    language: 'go',
  },
  {
    id: 'ionic',
    name: 'Ionic',
    type: 'framework',
    language: 'ionic',
    link: 'https://docs.sentry.io/platforms/javascript/guides/capacitor/',
  },
  {
    id: 'java',
    name: 'Java',
    type: 'language',
    language: 'java',
    link: 'https://docs.sentry.io/platforms/java/',
  },
  {
    id: 'java-log4j2',
    name: 'Log4j 2.x',
    type: 'framework',
    language: 'java',
    link: 'https://docs.sentry.io/platforms/java/guides/log4j2/',
  },
  {
    id: 'java-logback',
    name: 'Logback',
    type: 'framework',
    language: 'java',
    link: 'https://docs.sentry.io/platforms/java/guides/logback/',
  },
  {
    id: 'java-spring',
    name: 'Spring',
    type: 'framework',
    language: 'java',
    link: 'https://docs.sentry.io/platforms/java/guides/spring/',
  },
  {
    id: 'java-spring-boot',
    name: 'Spring Boot',
    type: 'framework',
    language: 'java',
    link: 'https://docs.sentry.io/platforms/java/guides/spring-boot/',
  },
  {
    id: 'javascript',
    name: 'Browser JavaScript',
    type: 'language',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/',
  },
  {
    id: 'javascript-angular',
    name: 'Angular',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/angular/',
  },
  {
    id: 'javascript-astro',
    name: 'Astro',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/astro/',
  },
  {
    id: 'javascript-ember',
    name: 'Ember',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/ember/',
  },
  {
    id: 'javascript-gatsby',
    name: 'Gatsby',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/gatsby/',
  },
  {
    id: 'javascript-nextjs',
    name: 'Next.js',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/nextjs/',
  },
  {
    id: 'javascript-nuxt',
    name: 'Nuxt',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/nuxt/',
  },
  {
    id: 'javascript-react',
    name: 'React',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/react/',
  },
  {
    id: 'javascript-remix',
    name: 'Remix',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/remix/',
  },
  {
    id: 'javascript-solid',
    name: 'Solid',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/solid/',
  },
  {
    id: 'javascript-solidstart',
    name: 'SolidStart',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/solidstart/',
  },
  {
    id: 'javascript-svelte',
    name: 'Svelte',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/svelte/',
  },
  {
    id: 'javascript-sveltekit',
    name: 'SvelteKit',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/sveltekit/',
  },
  {
    id: 'javascript-vue',
    name: 'Vue',
    type: 'framework',
    language: 'javascript',
    link: 'https://docs.sentry.io/platforms/javascript/guides/vue/',
  },
  {
    id: 'kotlin',
    name: 'Kotlin',
    type: 'language',
    language: 'kotlin',
    link: 'https://docs.sentry.io/platforms/kotlin/',
  },
  {
    id: 'minidump',
    name: 'Minidump',
    type: 'framework',
    language: 'minidump',
    link: 'https://docs.sentry.io/platforms/native/minidump/',
  },
  {
    id: 'native',
    name: 'Native',
    type: 'language',
    language: 'native',
    link: 'https://docs.sentry.io/platforms/native/',
  },
  {
    id: 'native-qt',
    name: 'Qt',
    type: 'framework',
    language: 'native',
    link: 'https://docs.sentry.io/platforms/native/guides/qt/',
  },
  {
    id: 'nintendo-switch',
    name: 'Nintendo Switch',
    type: 'framework',
    language: 'native',
    link: 'https://docs.sentry.io/platforms/nintendo-switch/',
  },
  {
    id: 'node',
    name: 'Node.js',
    type: 'language',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/node',
  },
  {
    id: 'node-awslambda',
    name: 'AWS Lambda (Node)',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/aws-lambda/',
  },
  {
    id: 'node-azurefunctions',
    name: 'Azure Functions (Node)',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/azure-functions/',
  },
  {
    id: 'node-connect',
    name: 'Connect',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/connect/',
  },
  {
    id: 'node-express',
    name: 'Express',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/express/',
  },
  {
    id: 'node-fastify',
    name: 'Fastify',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/fastify/',
  },
  {
    id: 'node-hapi',
    name: 'Hapi',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/hapi/',
  },
  {
    id: 'node-gcpfunctions',
    name: 'Google Cloud Functions (Node)',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/gcp-functions/',
  },
  {
    id: 'node-koa',
    name: 'Koa',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/koa/',
  },
  {
    id: 'node-nestjs',
    name: 'Nest.js',
    type: 'framework',
    language: 'node',
    link: 'https://docs.sentry.io/platforms/javascript/guides/nestjs/',
  },
  {
    id: 'php',
    name: 'PHP',
    type: 'language',
    language: 'php',
    link: 'https://docs.sentry.io/platforms/php/',
  },
  {
    id: 'php-laravel',
    name: 'Laravel',
    type: 'framework',
    language: 'php',
    link: 'https://docs.sentry.io/platforms/php/guides/laravel/',
  },
  {
    id: 'php-symfony',
    name: 'Symfony',
    type: 'framework',
    language: 'php',
    link: 'https://docs.sentry.io/platforms/php/guides/symfony/',
  },
  {
    id: 'powershell',
    name: 'PowerShell',
    type: 'language',
    language: 'powershell',
    link: 'https://docs.sentry.io/platforms/powershell/',
  },
  {
    id: 'python',
    name: 'Python',
    type: 'language',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/',
  },
  {
    id: 'python-aiohttp',
    name: 'AIOHTTP',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/aiohttp/',
  },
  {
    id: 'python-asgi',
    name: 'ASGI',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/asgi/',
  },
  {
    id: 'python-awslambda',
    name: 'AWS Lambda (Python)',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/aws-lambda/',
  },
  {
    id: 'python-bottle',
    name: 'Bottle',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/bottle/',
  },
  {
    id: 'python-celery',
    name: 'Celery',
    type: 'library',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/celery/',
  },
  {
    id: 'python-chalice',
    name: 'Chalice',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/chalice/',
  },
  {
    id: 'python-django',
    name: 'Django',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/django/',
  },
  {
    id: 'python-falcon',
    name: 'Falcon',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/falcon/',
  },
  {
    id: 'python-fastapi',
    name: 'FastAPI',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/fastapi/',
  },
  {
    id: 'python-flask',
    name: 'Flask',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/flask/',
  },
  {
    id: 'python-gcpfunctions',
    name: 'Google Cloud Functions (Python)',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/gcp-functions/',
  },
  {
    id: 'python-pylons',
    name: 'Pylons',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/legacy-sdk/integrations/pylons/',
  },
  {
    id: 'python-pymongo',
    name: 'PyMongo',
    type: 'library',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/pymongo/',
  },
  {
    id: 'python-pyramid',
    name: 'Pyramid',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/pyramid/',
  },
  {
    id: 'python-quart',
    name: 'Quart',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/quart/',
  },
  {
    id: 'python-rq',
    name: 'RQ (Redis Queue)',
    type: 'library',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/rq/',
  },
  {
    id: 'python-sanic',
    name: 'Sanic',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/sanic/',
  },
  {
    id: 'python-serverless',
    name: 'Serverless (Python)',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/serverless/',
  },
  {
    id: 'python-starlette',
    name: 'Starlette',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/starlette/',
  },
  {
    id: 'python-tornado',
    name: 'Tornado',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/tornado/',
  },
  {
    id: 'python-tryton',
    name: 'Tryton',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/tryton/',
  },
  {
    id: 'python-wsgi',
    name: 'WSGI',
    type: 'framework',
    language: 'python',
    link: 'https://docs.sentry.io/platforms/python/guides/wsgi/',
  },
  {
    id: 'react-native',
    name: 'React Native',
    type: 'language',
    language: 'react-native',
    link: 'https://docs.sentry.io/platforms/react-native/',
  },
  {
    id: 'ruby',
    name: 'Ruby',
    type: 'language',
    language: 'ruby',
    link: 'https://docs.sentry.io/platforms/ruby/',
  },
  {
    id: 'ruby-rack',
    name: 'Rack Middleware',
    type: 'framework',
    language: 'ruby',
    link: 'https://docs.sentry.io/platforms/ruby/guides/rack/',
  },
  {
    id: 'ruby-rails',
    name: 'Rails',
    type: 'framework',
    language: 'ruby',
    link: 'https://docs.sentry.io/platforms/ruby/guides/rails/',
  },
  {
    id: 'rust',
    name: 'Rust',
    type: 'language',
    language: 'rust',
    link: 'https://docs.sentry.io/platforms/rust/',
  },
  {
    id: 'unity',
    name: 'Unity',
    type: 'framework',
    language: 'unity',
    link: 'https://docs.sentry.io/platforms/unity/',
  },
  {
    id: 'unreal',
    name: 'Unreal Engine',
    type: 'framework',
    language: 'unreal',
    link: 'https://docs.sentry.io/platforms/unreal/',
  },
];

export const otherPlatform: PlatformIntegration = {
  id: 'other',
  name: 'Other',
  type: 'language',
  language: 'other',
  link: 'https://docs.sentry.io/platforms/',
};

/**
 * Array of all platforms that are displayed in the project creation flow.
 */
const allPlatforms = [...platforms, otherPlatform];

export default allPlatforms;
