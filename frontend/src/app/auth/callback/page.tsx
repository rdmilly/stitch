'use client';

import { Suspense } from 'react';
import CallbackHandler from './handler';

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-[#0f0f17]"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div></div>}>
      <CallbackHandler />
    </Suspense>
  );
}
