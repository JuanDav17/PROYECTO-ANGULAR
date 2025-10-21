import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module'; // Importa tu módulo principal

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));