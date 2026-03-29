import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import fs from 'fs';
import path from 'path';
import { App } from '@/components/app';
import { getAppConfig } from '@/lib/utils';

export default async function Page() {
  const configPath = path.join(process.cwd(), '..', 'user_config.json');

  if (!fs.existsSync(configPath)) {
    redirect('/setup');
  }

  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} />;
}
