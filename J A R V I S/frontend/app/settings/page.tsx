'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toastAlert } from '@/components/alert-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { GOOGLE_VOICES, OPENAI_VOICES } from '@/lib/voice_constants';

export default function SettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [formData, setFormData] = useState({
    user_id: '', // Internal ID (Hidden)
    user_name: '',
    assistant_name: 'Jarvis',
    llm_provider: 'google',
    llm_model: 'gemini-2.5-flash-native-audio-preview-09-2025',
    llm_voice: 'Puck',
    api_key: '',
    livekit_url: '',
    livekit_key: '',
    livekit_secret: '',
    mem0_key: '',
    google_search_key: '',
    search_engine_id: '',
    openweather_key: '',
    mds_enabled: true,
  });

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch('/api/config');
        const data = await res.json();
        if (data.exists) {
          setFormData({
            user_id: data.user_id || '', // Preserve existing ID
            user_name: data.user_name || '',
            assistant_name: data.assistant_name || 'Jarvis',
            llm_provider: data.llm?.provider || 'google',
            llm_model: data.llm?.model || 'gemini-2.5-flash-native-audio-preview-09-2025',
            llm_voice: data.llm?.voice || 'Puck',
            api_key: data.api_keys?.[data.llm?.provider || 'google'] || '',
            livekit_url: data.api_keys?.livekit_url || '',
            livekit_key: data.api_keys?.livekit_key || '',
            livekit_secret: data.api_keys?.livekit_secret || '',
            mem0_key: data.api_keys?.mem0 || '',
            google_search_key: data.api_keys?.google_search || '',
            search_engine_id: data.api_keys?.search_engine_id || '',
            openweather_key: data.api_keys?.openweather || '',
            mds_enabled: data.experiments?.mds_enabled ?? true,
          });
        } else {
          // ARGUMENT: NO CONFIG FOUND -> REDIRECT TO SETUP
          toastAlert({ title: 'NO CONFIGURATION', description: 'Redirecting to setup...' });
          router.push('/setup');
        }
      } catch (error) {
        console.error('Failed to load config', error);
        toastAlert({ title: 'Error', description: 'Failed to load existing configuration.' });
      } finally {
        setFetching(false);
      }
    };

    fetchConfig();
  }, [router]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleProviderChange = (value: string) => {
    const isGoogle = value === 'google';
    setFormData({
      ...formData,
      llm_provider: value,
      llm_model: isGoogle
        ? 'gemini-2.5-flash-native-audio-preview-09-2025'
        : 'gpt-4o-realtime-preview',
      llm_voice: isGoogle ? 'Puck' : 'alloy',
      api_key: '',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const configData = {
        user_id: formData.user_id, // Pass back the internal ID
        user_name: formData.user_name,
        assistant_name: formData.assistant_name,
        llm: {
          provider: formData.llm_provider,
          model: formData.llm_model,
          voice: formData.llm_voice,
        },
        api_keys: {
          [formData.llm_provider]: formData.api_key,
          livekit_url: formData.livekit_url,
          livekit_key: formData.livekit_key,
          livekit_secret: formData.livekit_secret,
          mem0: formData.mem0_key,
          google_search: formData.google_search_key,
          search_engine_id: formData.search_engine_id,
          openweather: formData.openweather_key,
        },
        experiments: {
          mds_enabled: formData.mds_enabled,
        },
      };

      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configData),
      });

      if (!res.ok) throw new Error('Failed to save configuration');

      toastAlert({
        title: 'PROTOCOL UPDATED',
        description: 'System configuration saved successfully.',
      });
      setTimeout(() => router.push('/'), 1000);
    } catch {
      toastAlert({ title: 'ERROR', description: 'Failed to save configuration.' });
    } finally {
      setLoading(false);
    }
  };

  // Helper to get available voices
  const currentVoices = formData.llm_provider === 'google' ? GOOGLE_VOICES : OPENAI_VOICES;

  if (fetching) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black font-mono tracking-widest text-cyan-400 uppercase">
        <div className="animate-pulse">Initializing System Protocols...</div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-black font-mono text-white selection:bg-cyan-500/30">
      {/* Background Effects */}
      <div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black opacity-80" />
      <div className="pointer-events-none fixed top-0 left-0 z-0 h-full w-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03]" />

      {/* Rotating HUD Rings (Pure CSS Simulation) */}
      <div className="pointer-events-none fixed top-1/2 left-1/2 z-0 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 animate-[spin_60s_linear_infinite] rounded-full border border-cyan-900/30" />
      <div className="pointer-events-none fixed top-1/2 left-1/2 z-0 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 animate-[spin_40s_linear_infinite_reverse] rounded-full border border-cyan-900/20" />

      <div className="relative z-10 container mx-auto max-w-3xl px-4 py-8">
        {/* Header */}
        <header className="mb-12 flex items-center justify-between border-b border-cyan-500/30 pb-6 backdrop-blur-sm">
          <div>
            <h1
              className="bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-4xl font-bold tracking-tight text-transparent uppercase"
              style={{ textShadow: '0 0 20px rgba(6,182,212,0.5)' }}
            >
              J.A.R.V.I.S.
            </h1>
            <p className="mt-1 text-xs tracking-[0.2em] text-cyan-600">
              SYSTEM CONFIGURATION INTERFACE // V2.0
            </p>
          </div>
          <Button
            variant="ghost"
            className="border border-cyan-900 text-cyan-400 transition-all duration-300 hover:border-cyan-400 hover:bg-cyan-950/30 hover:text-cyan-200"
            onClick={() => router.push('/')}
          >
            {'< RETURN TO DASHBOARD'}
          </Button>
        </header>

        <form
          onSubmit={handleSubmit}
          className="animate-in fade-in slide-in-from-bottom-4 space-y-8 duration-700"
        >
          {/* Identity Module */}
          <div className="group relative rounded-xl border border-cyan-500/20 bg-slate-950/50 p-6 shadow-[0_0_15px_rgba(6,182,212,0.05)] backdrop-blur-md transition-all hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-cyan-800 opacity-50">
              IDENTITY_MODULE
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label
                  htmlFor="user_id"
                  className="flex justify-between text-xs tracking-wider text-cyan-100 uppercase"
                >
                  <span>User Name</span>
                  <span className="rounded border border-cyan-900/50 bg-cyan-950/50 px-2 py-0.5 text-[10px] text-cyan-800">
                    PERMANENT • LOCKED
                  </span>
                </Label>
                <Input
                  id="user_id"
                  name="user_id"
                  value={formData.user_id || 'AUTO-GENERATING...'}
                  readOnly
                  disabled
                  className="cursor-not-allowed border-cyan-900/50 bg-black/60 font-mono text-sm tracking-widest text-cyan-500 select-all"
                />
              </div>

              <div className="space-y-2">
                <Label
                  htmlFor="user_name"
                  className="text-xs tracking-wider text-cyan-100 uppercase"
                >
                  Full Name <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  id="user_name"
                  name="user_name"
                  placeholder="ENTER DESIGNATION"
                  required
                  value={formData.user_name}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 text-cyan-300 transition-all placeholder:text-cyan-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                />
              </div>

              <div className="space-y-2">
                <Label
                  htmlFor="assistant_name"
                  className="text-xs tracking-wider text-cyan-100 uppercase"
                >
                  Assistant Name
                </Label>
                <Input
                  id="assistant_name"
                  name="assistant_name"
                  placeholder="e.g. JARVIS"
                  value={formData.assistant_name}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 text-cyan-300 transition-all placeholder:text-cyan-900 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                />
              </div>

              <div className="flex items-center justify-between rounded-lg border border-cyan-900/60 bg-black/40 px-4 py-4">
                <div className="space-y-1">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    MDS Adaptive Personalization
                  </Label>
                  <p className="text-xs text-cyan-700">
                    Keep this on for adaptive runs, or turn it off for baseline evaluation.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={formData.mds_enabled}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      mds_enabled: e.target.checked,
                    }))
                  }
                  className="h-5 w-5 accent-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Neural Interface (LLM) */}
          <div className="relative rounded-xl border border-cyan-500/20 bg-slate-950/50 p-6 shadow-[0_0_15px_rgba(6,182,212,0.05)] backdrop-blur-md transition-all hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-cyan-800 opacity-50">
              NEURAL_CORE
            </div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label
                  htmlFor="llm_provider"
                  className="text-xs tracking-wider text-cyan-100 uppercase"
                >
                  Select Model <span className="ml-1 text-red-500">*</span>
                </Label>
                <Select value={formData.llm_provider} onValueChange={handleProviderChange}>
                  <SelectTrigger className="border-cyan-900 bg-black/40 text-cyan-300">
                    <SelectValue placeholder="SELECT CORE" />
                  </SelectTrigger>
                  <SelectContent className="border-cyan-500/50 bg-slate-950 text-cyan-300">
                    <SelectItem value="google">GOOGLE GEMINI</SelectItem>
                    <SelectItem value="openai">OPENAI</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="llm_model"
                  className="text-xs tracking-wider text-cyan-100 uppercase"
                >
                  Model Name <span className="ml-1 text-red-500">*</span>
                </Label>
                <Select
                  value={formData.llm_model}
                  onValueChange={(val) => setFormData({ ...formData, llm_model: val })}
                >
                  <SelectTrigger className="h-auto border-cyan-900 bg-black/40 py-2 text-left text-cyan-300 [&>span]:break-words [&>span]:whitespace-normal">
                    <SelectValue placeholder="SELECT ARCHITECTURE" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[200px] border-cyan-500/50 bg-slate-950 text-cyan-300">
                    {formData.llm_provider === 'google' ? (
                      <>
                        <SelectItem value="gemini-2.0-flash-exp">gemini-2.0-flash-exp</SelectItem>
                        <SelectItem value="gemini-2.0-flash-live-001">
                          gemini-2.0-flash-live-001
                        </SelectItem>
                        <SelectItem value="gemini-2.5-flash-native-audio-preview-09-2025">
                          gemini-2.5-flash-native-audio-preview-09-2025
                        </SelectItem>
                        <SelectItem value="gemini-2.5-flash-native-audio-preview-12-2025">
                          gemini-2.5-flash-native-audio-preview-12-2025
                        </SelectItem>
                        <SelectItem value="gemini-live-2.5-flash-native-audio">
                          gemini-live-2.5-flash-native-audio
                        </SelectItem>
                        <SelectItem value="gemini-live-2.5-flash-preview">
                          gemini-live-2.5-flash-preview
                        </SelectItem>
                        <SelectItem value="gemini-live-2.5-flash-preview-native-audio">
                          gemini-live-2.5-flash-preview-native-audio
                        </SelectItem>
                        <SelectItem value="gemini-live-2.5-flash-preview-native-audio-09-2025">
                          gemini-live-2.5-flash-preview-native-audio-09-2025
                        </SelectItem>
                      </>
                    ) : (
                      <>
                        <SelectItem value="gpt-4o-realtime-preview">
                          gpt-4o-realtime-preview
                        </SelectItem>
                        <SelectItem value="gpt-realtime">gpt-realtime</SelectItem>
                        <SelectItem value="gpt-realtime-2025-08-28">
                          gpt-realtime-2025-08-28
                        </SelectItem>
                      </>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                  Select Voice <span className="ml-1 text-red-500">*</span>
                </Label>
                <Select
                  value={formData.llm_voice}
                  onValueChange={(val) => setFormData({ ...formData, llm_voice: val })}
                >
                  <SelectTrigger className="border-cyan-900 bg-black/40 text-cyan-300">
                    <SelectValue placeholder="Select Voice" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[300px] border-cyan-500/50 bg-slate-950 text-cyan-300">
                    <div className="px-2 py-1.5 text-xs font-semibold text-cyan-700/80">MALE</div>
                    {currentVoices.male.map((v) => (
                      <SelectItem key={v} value={v}>
                        {v}
                      </SelectItem>
                    ))}
                    <div className="mt-2 px-2 py-1.5 text-xs font-semibold text-cyan-700/80">
                      FEMALE
                    </div>
                    {currentVoices.female.map((v) => (
                      <SelectItem key={v} value={v}>
                        {v}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="api_key" className="text-xs tracking-wider text-cyan-100 uppercase">
                  Model API <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  id="api_key"
                  name="api_key"
                  type="password"
                  required
                  value={formData.api_key}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 font-mono tracking-tighter text-cyan-300"
                />
              </div>
            </div>
          </div>

          {/* Uplink (LiveKit) */}
          <div className="relative rounded-xl border border-cyan-500/20 bg-slate-950/50 p-6 shadow-[0_0_15px_rgba(6,182,212,0.05)] backdrop-blur-md transition-all hover:shadow-[0_0_20px_rgba(6,182,212,0.1)]">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-cyan-800 opacity-50">
              SATELLITE_UPLINK
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                  LiveKit URL <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  name="livekit_url"
                  required
                  value={formData.livekit_url}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 font-mono text-cyan-300"
                />
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    Access Key <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Input
                    name="livekit_key"
                    type="password"
                    required
                    value={formData.livekit_key}
                    onChange={handleInputChange}
                    className="border-cyan-900 bg-black/40 font-mono text-cyan-300"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    Secret Key <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Input
                    name="livekit_secret"
                    type="password"
                    required
                    value={formData.livekit_secret}
                    onChange={handleInputChange}
                    className="border-cyan-900 bg-black/40 font-mono text-cyan-300"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Memory Core */}
          <div className="relative rounded-xl border border-purple-500/20 bg-slate-950/50 p-6 shadow-[0_0_15px_rgba(168,85,247,0.05)] backdrop-blur-md transition-all hover:shadow-[0_0_20px_rgba(168,85,247,0.1)]">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-purple-800 opacity-50">
              MEMORY_BANKS
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="mem0_key"
                className="text-xs tracking-wider text-purple-100 uppercase"
              >
                Mem0 Key (Long Term Storage) <span className="ml-1 text-red-500">*</span>
              </Label>
              <Input
                id="mem0_key"
                name="mem0_key"
                type="password"
                value={formData.mem0_key}
                onChange={handleInputChange}
                className="border-purple-900 bg-black/40 font-mono text-purple-300 focus:border-purple-400 focus:ring-purple-400"
              />
            </div>
          </div>

          {/* External Tools */}
          <div className="relative rounded-xl border border-yellow-500/20 bg-slate-950/50 p-6 shadow-[0_0_15px_rgba(234,179,8,0.05)] backdrop-blur-md transition-all hover:shadow-[0_0_20px_rgba(234,179,8,0.1)]">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-yellow-800 opacity-50">
              EXTERNAL_SENSORS
            </div>
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label
                  htmlFor="google_search_key"
                  className="text-xs tracking-wider text-yellow-100 uppercase"
                >
                  Google Custom Search Key
                </Label>
                <Input
                  id="google_search_key"
                  name="google_search_key"
                  type="password"
                  value={formData.google_search_key}
                  onChange={handleInputChange}
                  className="border-yellow-900 bg-black/40 font-mono text-yellow-300 focus:border-yellow-400"
                />
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="search_engine_id"
                  className="text-xs tracking-wider text-yellow-100 uppercase"
                >
                  Search Engine ID
                </Label>
                <Input
                  id="search_engine_id"
                  name="search_engine_id"
                  value={formData.search_engine_id}
                  onChange={handleInputChange}
                  className="border-yellow-900 bg-black/40 font-mono text-yellow-300 focus:border-yellow-400"
                />
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="openweather_key"
                  className="text-xs tracking-wider text-yellow-100 uppercase"
                >
                  OpenWeather Key <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  id="openweather_key"
                  name="openweather_key"
                  type="password"
                  required
                  value={formData.openweather_key}
                  onChange={handleInputChange}
                  className="border-yellow-900 bg-black/40 font-mono text-yellow-300 focus:border-yellow-400"
                />
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-4 pt-8">
            <Button
              type="submit"
              className="w-full border border-cyan-400/50 bg-cyan-600 py-6 font-bold tracking-widest text-white uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all duration-300 hover:bg-cyan-500 hover:shadow-[0_0_40px_rgba(6,182,212,0.6)] disabled:cursor-not-allowed disabled:border-slate-700 disabled:bg-slate-800 disabled:text-slate-500 disabled:opacity-50 disabled:shadow-none"
              disabled={
                loading ||
                !(
                  formData.user_name &&
                  formData.api_key &&
                  formData.livekit_url &&
                  formData.livekit_key &&
                  formData.livekit_secret &&
                  formData.mem0_key &&
                  formData.openweather_key
                )
              }
            >
              {loading ? 'INITIATING UPLOAD...' : 'INITIALIZE SYSTEM PROTOCOLS'}
            </Button>

            <div className="mt-4 flex w-full justify-center">
              <button
                type="button"
                className="text-[10px] font-bold tracking-widest text-red-900 uppercase transition-colors hover:text-red-500"
                onClick={async () => {
                  if (
                    confirm('WARNING: COMPLETE SYSTEM RESET. ALL DATA WILL BE PURGED. CONFIRM?')
                  ) {
                    try {
                      const res = await fetch('/api/config', { method: 'DELETE' });
                      if (res.ok) {
                        toastAlert({
                          title: 'SYSTEM PURGED',
                          description: 'Configuration deleted. Rebooting...',
                        });
                        window.location.href = '/';
                      } else {
                        throw new Error('Reset failed');
                      }
                    } catch {
                      toastAlert({ title: 'ERROR', description: 'Purge sequence failed.' });
                    }
                  }
                }}
              >
                [ INITIATE FACTORY RESET ]
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Corner Decorative Elements */}
      <div className="pointer-events-none fixed top-0 left-0 h-32 w-32 rounded-tl-3xl border-t-2 border-l-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed top-0 right-0 h-32 w-32 rounded-tr-3xl border-t-2 border-r-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed bottom-0 left-0 h-32 w-32 rounded-bl-3xl border-b-2 border-l-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed right-0 bottom-0 h-32 w-32 rounded-br-3xl border-r-2 border-b-2 border-cyan-500/20" />
    </div>
  );
}
