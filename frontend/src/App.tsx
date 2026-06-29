import { useEffect, useState } from "react";
import "./App.css";
import {
  clearToken,
  getCurrentUser,
  hasToken,
} from "./api/client";
import { Chat } from "./components/Chat";
import { Header } from "./components/Header";
import { LoginForm } from "./components/LoginForm";
import type { User } from "./types";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [guestMode, setGuestMode] = useState(false);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    if (!hasToken()) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      setGuestMode(false);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUser();
  }, []);

  function handleLogout() {
    clearToken();
    setUser(null);
    setGuestMode(false);
  }

  const canUseChat = Boolean(user) || guestMode;

  if (loading) {
    return <main className="page">Loading...</main>;
  }

  return (
    <main className="page">
      <Header
        user={user}
        onLogout={handleLogout}
        guestMode={guestMode}
        onSkipLogin={() => setGuestMode(true)}
      />

      {!canUseChat ? (
        <LoginForm
          onSuccess={() => {
            setLoading(true);
            void loadUser();
          }}
        />
      ) : (
        <Chat userId={user?.id} />
      )}
    </main>
  );
}
