"use client";

import Image from "next/image";
import { useState } from "react";
import { supabase } from "../utils/supabaseClient";

export default function Home() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAuth, setShowAuth] = useState(false);

  async function signUp() {
    setError(null);
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });
    if (error) setError(error.message);
    else {
      setUser(data.user);
      if (username) {
        await supabase.from('profiles').insert([
          {
            id: data?.user?.id,
            username,
            status: 'free',
          },
        ]);
      }
    }
  }

  async function signIn() {
    setError(null);
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) setError(error.message);
    else setUser(data.user);
  }

  async function signOut() {
    await supabase.auth.signOut();
    setUser(null);
  }

  // Landing page if not signed in and not showing auth form
  if (!user && !showAuth) {
    return (
      <div className="min-h-screen flex flex-col">
        {/* Header */}
        <header className="flex justify-between items-center px-8 py-6 w-full">
          <span className="text-xl font-semibold">Stock Picker</span>
          <nav className="flex gap-8 text-gray-700 text-base">
            <a href="#learn" className="hover:underline">Learn More</a>
            <a href="#pricing" className="hover:underline">Pricing</a>
            <button className="hover:underline" onClick={() => setShowAuth(true)}>Sign In</button>
          </nav>
        </header>
        {/* Main Content */}
        <main className="flex flex-1 flex-col items-center justify-center text-center px-4">
          <h1 className="text-4xl sm:text-6xl font-bold mb-6 text-black">Invest in european small caps<br />the smart way.</h1>
          <p className="text-lg sm:text-xl text-gray-700 mb-10 max-w-xl mx-auto">
            A tool to help you pick your next small cap investment from more than 50k stocks in europe.
          </p>
          <button
            className="bg-gradient-to-r from-green-400 to-green-600 text-white text-lg font-semibold px-12 py-4 rounded-xl shadow hover:scale-105 transition mb-2"
            onClick={() => setShowAuth(true)}
          >
            Sign Up
          </button>
        </main>
      </div>
    );
  }

  // Auth form or signed in view
  return (
    <div className="font-sans grid grid-rows-[auto_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      {/* Landing Section */}
      <section className="w-full max-w-xl bg-white rounded-lg shadow-md p-8 mb-8 flex flex-col items-center gap-4 row-start-1">
        <Image
          className="mb-2"
          src="/next.svg"
          alt="Next.js logo"
          width={120}
          height={26}
          priority
        />
        <h1 className="text-3xl font-bold text-center text-black">Stock Picker</h1>
        <p className="text-center text-black">
          <b>Stock Picker</b> is a modern web app for discovering, analyzing, and tracking stocks. Built with Next.js and Supabase, it features real-time data, secure authentication, and a clean, responsive UI.
        </p>
        <ul className="list-disc list-inside text-black text-sm mt-2">
          <li>🔒 Supabase Auth for secure sign-in/sign-up</li>
          <li>📈 Real-time stock data (coming soon)</li>
          <li>⚡ Fast, modern Next.js frontend</li>
        </ul>
      </section>
      {/* Auth Section */}
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-full max-w-md bg-white rounded-lg shadow p-8">
        <h2 className="text-xl font-semibold mb-4 text-center w-full text-black">Sign in to your account</h2>
        {user ? (
          <div className="flex flex-col gap-2 items-center text-black">
            <span>Signed in as: {user.email}</span>
            <button className="bg-red-500 text-white px-4 py-2 rounded" onClick={signOut}>
              Sign Out
            </button>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              signIn();
            }}
            className="flex flex-col gap-2 w-full"
          >
            <input
              className="border border-black px-2 py-1 rounded text-black bg-white placeholder-gray-500"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              className="border border-black px-2 py-1 rounded text-black bg-white placeholder-gray-500"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <input
              className="border border-black px-2 py-1 rounded text-black bg-white placeholder-gray-500"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <div className="flex gap-2">
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded"
                type="submit"
              >
                Sign In
              </button>
              <button
                className="bg-green-500 text-white px-4 py-2 rounded"
                type="button"
                onClick={signUp}
              >
                Sign Up
              </button>
            </div>
            {error && <span className="text-red-500">{error}</span>}
          </form>
        )}
      </main>
      {/* Footer */}
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
