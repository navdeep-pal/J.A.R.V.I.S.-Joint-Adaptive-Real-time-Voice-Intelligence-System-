'use client';

import { useState } from 'react';
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

export default function SetupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    user_id: '',
    user_name: '',
    assistant_name: 'Jarvis', // Default Value
    llm_provider: 'google',
    llm_model: 'gemini-live-2.5-flash-preview-native-audio-09-2025',
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleProviderChange = (value: string) => {
    const isGoogle = value === 'google';
    setFormData({
      ...formData,
      llm_provider: value,
      llm_model: isGoogle
        ? 'gemini-live-2.5-flash-preview-native-audio-09-2025'
        : 'gpt-4o-realtime-preview',
      llm_voice: isGoogle ? 'Puck' : 'alloy',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const configData = {
        user_id: formData.user_id, // Use explicit input
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
        title: 'SYSTEM ONLINE',
        description: `Initialization complete. Launching ${formData.assistant_name || 'System'}...`,
      });

      // Artificial delay for UX
      setTimeout(() => router.push('/'), 1500);
    } catch {
      toastAlert({ title: 'ERROR', description: 'Initialization failed. Check inputs.' });
    } finally {
      setLoading(false);
    }
  };

  // Helper to get available voices
  const currentVoices = formData.llm_provider === 'google' ? GOOGLE_VOICES : OPENAI_VOICES;

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-x-hidden bg-black p-4 font-mono text-white selection:bg-cyan-500/30">
      {/* Background Effects */}
      <div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black opacity-80" />
      <div className="pointer-events-none fixed top-0 left-0 z-0 h-full w-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03]" />

      {/* Rotating HUD Rings */}
      <div className="pointer-events-none fixed top-1/2 left-1/2 z-0 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 animate-[spin_60s_linear_infinite] rounded-full border border-cyan-900/30" />
      <div className="pointer-events-none fixed top-1/2 left-1/2 z-0 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 animate-[spin_40s_linear_infinite_reverse] rounded-full border border-cyan-900/20" />

      <div className="relative z-10 w-full max-w-3xl">
        {/* Header */}
        <header className="animate-in fade-in slide-in-from-top-8 mb-12 text-center duration-700">
          <h1
            className="bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-5xl font-bold tracking-tight text-transparent uppercase"
            style={{ textShadow: '0 0 20px rgba(6,182,212,0.5)' }}
          >
            {formData.assistant_name ? formData.assistant_name.split('').join('.') : 'A.I.'}
          </h1>
          <p className="mt-2 text-xs tracking-[0.3em] text-cyan-600">
            INITIAL SYSTEM CONFIGURATION
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="animate-in fade-in zoom-in-95 space-y-8 delay-150 duration-700"
        >
          {/* Identity & Core Module Combined for Setup */}
          <div className="relative rounded-xl border border-cyan-500/20 bg-slate-950/80 p-8 shadow-[0_0_30px_rgba(6,182,212,0.1)] backdrop-blur-md">
            <div className="absolute top-0 left-0 h-1 w-full bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>
            <div className="space-y-6">
              {/* Identity Section */}
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <Label
                    htmlFor="user_id"
                    className="text-xs tracking-wider text-cyan-100 uppercase"
                  >
                    User Name <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Input
                    id="user_id"
                    name="user_id"
                    placeholder="unique_handle (e.g. gaurav_01)"
                    required
                    value={formData.user_id}
                    onChange={(e) => {
                      // Auto-fill display name if empty/matching
                      const newVal = e.target.value.replace(/[^a-zA-Z0-9_-]/g, '').toLowerCase();
                      setFormData((prev) => ({
                        ...prev,
                        user_id: newVal,
                        // Optional: Auto-suggest display name if currently empty
                        // user_name: prev.user_name ? prev.user_name : e.target.value
                      }));
                    }}
                    className="border-cyan-900 bg-black/50 py-6 font-mono text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400"
                  />
                  <p className="pl-1 text-[10px] tracking-widest text-cyan-700/80 uppercase">
                    ⚠️ CANNOT BE CHANGED LATER
                  </p>
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
                    placeholder="What should I call you?"
                    required
                    value={formData.user_name}
                    onChange={handleInputChange}
                    className="border-cyan-900 bg-black/50 py-6 font-sans text-lg text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400"
                  />
                  <p className="pl-1 text-[10px] tracking-widest text-cyan-700/80 uppercase">
                    EDITABLE ANYTIME
                  </p>
                </div>
              </div>

              {/* Assistant Name Input */}
              <div className="space-y-2">
                <Label
                  htmlFor="assistant_name"
                  className="text-xs tracking-wider text-cyan-100 uppercase"
                >
                  Assistant Name <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  id="assistant_name"
                  name="assistant_name"
                  placeholder="e.g. JARVIS"
                  required
                  value={formData.assistant_name}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/50 py-6 font-sans text-lg text-cyan-300 placeholder:text-cyan-900/50 focus:border-cyan-400"
                />
              </div>

              <div className="flex items-center justify-between rounded-lg border border-cyan-900/60 bg-black/40 px-4 py-4">
                <div className="space-y-1">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    MDS Adaptive Personalization
                  </Label>
                  <p className="text-xs text-cyan-700">
                    Enable for personalization experiment mode. Disable for baseline runs.
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

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    Select Model <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Select value={formData.llm_provider} onValueChange={handleProviderChange}>
                    <SelectTrigger className="border-cyan-900 bg-black/50 text-cyan-300">
                      <SelectValue placeholder="Select Provider" />
                    </SelectTrigger>
                    <SelectContent className="border-cyan-500/50 bg-slate-950 text-cyan-300">
                      <SelectItem value="google">GOOGLE GEMINI</SelectItem>
                      <SelectItem value="openai">OPENAI</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    Model Name <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Select
                    value={formData.llm_model}
                    onValueChange={(val) => setFormData({ ...formData, llm_model: val })}
                  >
                    <SelectTrigger className="h-auto border-cyan-900 bg-black/50 py-2 text-left text-cyan-300 [&>span]:break-words [&>span]:whitespace-normal">
                      <SelectValue placeholder="Select Model" />
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
                    <SelectTrigger className="border-cyan-900 bg-black/50 text-cyan-300">
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
                  <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                    Model API <span className="ml-1 text-red-500">*</span>
                  </Label>
                  <Input
                    id="api_key"
                    name="api_key"
                    type="password"
                    required
                    value={formData.api_key}
                    onChange={handleInputChange}
                    className="border-cyan-900 bg-black/50 font-mono text-cyan-300"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Infrastructure */}
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* LiveKit */}
            <div className="relative rounded-xl border border-cyan-500/20 bg-slate-950/50 p-6 backdrop-blur-md">
              <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-cyan-800 opacity-50">
                UPLINK
              </div>
              <div className="space-y-4">
                <Label className="text-xs tracking-wider text-cyan-100 uppercase">
                  Livekit API <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  name="livekit_url"
                  placeholder="URL"
                  required
                  value={formData.livekit_url}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 font-mono text-sm text-cyan-300"
                />
                <Input
                  name="livekit_key"
                  placeholder="API Key"
                  type="password"
                  required
                  value={formData.livekit_key}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 font-mono text-sm text-cyan-300"
                />
                <Input
                  name="livekit_secret"
                  placeholder="Secret Key"
                  type="password"
                  required
                  value={formData.livekit_secret}
                  onChange={handleInputChange}
                  className="border-cyan-900 bg-black/40 font-mono text-sm text-cyan-300"
                />
              </div>
            </div>

            {/* Memory */}
            <div className="relative rounded-xl border border-purple-500/20 bg-slate-950/50 p-6 backdrop-blur-md">
              <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-purple-800 opacity-50">
                MEMORY
              </div>
              <div className="space-y-4">
                <Label className="text-xs tracking-wider text-purple-100 uppercase">
                  Mem0 API Key <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  name="mem0_key"
                  type="password"
                  placeholder="REQUIRED"
                  required
                  value={formData.mem0_key}
                  onChange={handleInputChange}
                  className="border-purple-900 bg-black/40 font-mono text-sm text-purple-300 focus:border-purple-400"
                />
              </div>
            </div>
          </div>

          {/* External Tools (Optional) */}
          <div className="relative rounded-xl border border-yellow-500/20 bg-slate-950/50 p-6 opacity-80 backdrop-blur-md transition-opacity hover:opacity-100">
            <div className="absolute top-0 right-0 p-2 text-[10px] font-bold tracking-widest text-yellow-800 opacity-50">
              MODULES (OPT)
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label className="text-[10px] tracking-wider text-yellow-100 uppercase">
                  Google Search Key
                </Label>
                <Input
                  name="google_search_key"
                  type="password"
                  value={formData.google_search_key}
                  onChange={handleInputChange}
                  className="h-8 border-yellow-900 bg-black/40 font-mono text-xs text-yellow-300 focus:border-yellow-400"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] tracking-wider text-yellow-100 uppercase">
                  Engine ID
                </Label>
                <Input
                  name="search_engine_id"
                  value={formData.search_engine_id}
                  onChange={handleInputChange}
                  className="h-8 border-yellow-900 bg-black/40 font-mono text-xs text-yellow-300 focus:border-yellow-400"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-[10px] tracking-wider text-yellow-100 uppercase">
                  OpenWeather Key <span className="ml-1 text-red-500">*</span>
                </Label>
                <Input
                  name="openweather_key"
                  type="password"
                  required
                  value={formData.openweather_key}
                  onChange={handleInputChange}
                  className="h-8 border-yellow-900 bg-black/40 font-mono text-xs text-yellow-300 focus:border-yellow-400"
                />
              </div>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full border border-cyan-400/50 bg-cyan-600 py-8 text-lg font-bold tracking-widest text-white uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all duration-300 hover:bg-cyan-500 hover:shadow-[0_0_40px_rgba(6,182,212,0.6)] disabled:cursor-not-allowed disabled:border-slate-700 disabled:bg-slate-800 disabled:text-slate-500 disabled:opacity-50 disabled:shadow-none"
            disabled={
              loading ||
              !(
                formData.user_id &&
                formData.user_name &&
                formData.assistant_name &&
                formData.api_key &&
                formData.livekit_url &&
                formData.livekit_key &&
                formData.livekit_secret &&
                formData.mem0_key &&
                formData.openweather_key
              )
            }
          >
            {loading
              ? 'INITIALIZING...'
              : `ACTIVATE ${formData.assistant_name ? formData.assistant_name.toUpperCase() : 'SYSTEM'} PROTOCOLS`}
          </Button>
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
