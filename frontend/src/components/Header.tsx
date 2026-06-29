import type { User } from "../types";

interface HeaderProps {
  user: User | null;
  onLogout: () => void;
  guestMode: boolean;
  onSkipLogin: () => void;
}

export function Header({
  user,
  onLogout,
  guestMode,
  onSkipLogin,
}: HeaderProps) {
  return (
    <header className="header">
      <div>
        <p className="eyebrow">E-Commerce AI Agent</p>
        <h1>Business Assistant</h1>
      </div>

      <div className="header-actions">
        {user ? (
          <>
            <span className="user-pill">
              {user.full_name || user.email}
            </span>
            <button type="button" className="secondary" onClick={onLogout}>
              Log out
            </button>
          </>
        ) : guestMode ? (
          <span className="user-pill">Guest mode</span>
        ) : (
          <button type="button" className="secondary" onClick={onSkipLogin}>
            Continue without login
          </button>
        )}
      </div>
    </header>
  );
}
