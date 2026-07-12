import { useMemo, useState } from "react";
import {
  ArrowRight,
  Building2,
  CheckCircle2,
  ShieldCheck,
  Loader2,
  TriangleAlert,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { ROUTE_PATHS } from "../../routes/routePaths";
import { USER_ROLES } from "../../constants/roles";
import useAuth from "../../hooks/useAuth";

const demoAccounts = [
  {
    label: "Admin Demo",
    role: USER_ROLES.admin,
    accent: "from-sky-500 to-cyan-400",
  },
  {
    label: "Manager Demo",
    role: USER_ROLES.assetManager,
    accent: "from-indigo-500 to-blue-500",
  },
  {
    label: "Employee Demo",
    role: USER_ROLES.employee,
    accent: "from-emerald-500 to-teal-400",
  },
];

export default function Login() {
  const navigate = useNavigate();
  const auth = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const demoUsersByRole = useMemo(
    () =>
      auth.demoUsers.reduce((accumulator, user) => {
        accumulator[user.role] = user;
        return accumulator;
      }, {}),
    [auth.demoUsers],
  );

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setErrorMessage("");

    const result = await auth.login({ email, password, rememberMe });

    if (!result.success) {
      setErrorMessage(result.message);
      setIsSubmitting(false);
      return;
    }

    navigate(getDashboardPath(result.role), { replace: true });
  }

  async function handleDemoLogin(role) {
    const demoUser = demoUsersByRole[role];

    if (!demoUser) {
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    const result = await auth.login({
      email: demoUser.email,
      password: demoUser.password,
      rememberMe: true,
    });

    if (!result.success) {
      setErrorMessage(result.message);
      setIsSubmitting(false);
      return;
    }

    navigate(getDashboardPath(result.role), { replace: true });
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#1d4ed8_0%,_#0f172a_38%,_#020617_100%)] px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-7xl overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/35 shadow-2xl shadow-slate-950/40 backdrop-blur-xl lg:grid-cols-[1.15fr_0.85fr]">
        <section className="relative hidden overflow-hidden border-r border-white/10 p-8 lg:flex lg:flex-col lg:justify-between xl:p-12">
          <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(15,23,42,0.25),rgba(14,165,233,0.12),rgba(15,23,42,0.45))]" />
          <div className="absolute -left-20 top-16 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl" />
          <div className="absolute bottom-0 right-0 h-80 w-80 rounded-full bg-blue-500/20 blur-3xl" />

          <div className="relative z-10 max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-cyan-100/90">
              <Building2 size={14} />
              AssetFlow Enterprise
            </div>
            <h1 className="mt-6 max-w-lg text-5xl font-semibold leading-tight tracking-tight text-white xl:text-6xl">
              Modern asset operations for ambitious teams.
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300 xl:text-lg">
              Secure access, clear accountability, and a polished interface built
              for IT, operations, and leadership in one place.
            </p>
          </div>

          <div className="relative z-10 grid max-w-2xl gap-4 sm:grid-cols-2">
            <FeatureCard
              title="Enterprise-ready visibility"
              description="Track allocations, approvals, and service requests with confidence."
              icon={<ShieldCheck size={18} />}
            />
            <FeatureCard
              title="Fast day-one onboarding"
              description="Demo accounts let stakeholders jump into the experience instantly."
              icon={<CheckCircle2 size={18} />}
            />
          </div>
        </section>

        <section className="flex items-center justify-center p-4 sm:p-6 lg:p-8">
          <div className="w-full max-w-lg rounded-[1.75rem] border border-white/10 bg-white/95 p-6 text-slate-900 shadow-[0_24px_80px_rgba(2,6,23,0.45)] shadow-cyan-950/20 sm:p-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-700">
                Welcome back
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
                Sign in to AssetFlow
              </h2>
              <p className="mt-3 max-w-md text-sm leading-6 text-slate-600">
                Use your enterprise credentials to continue. Demo access is
                available below for quick exploration.
              </p>
            </div>

            <form className="space-y-5" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-500/10"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <label htmlFor="password" className="text-sm font-medium text-slate-700">
                    Password
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-sm font-medium text-sky-700 transition hover:text-sky-800"
                  >
                    Forgot password?
                  </Link>
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-sky-500 focus:bg-white focus:ring-4 focus:ring-sky-500/10"
                />
              </div>

              <div className="flex items-center justify-between gap-4">
                <label className="inline-flex items-center gap-3 text-sm font-medium text-slate-600">
                  <input
                    checked={rememberMe}
                    onChange={(event) => setRememberMe(event.target.checked)}
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-sky-600 accent-sky-600 focus:ring-sky-500"
                  />
                  Remember me
                </label>
                <span className="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
                  Session ready
                </span>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-600 to-blue-600 px-5 text-sm font-semibold text-white shadow-lg shadow-sky-600/25 transition hover:from-sky-500 hover:to-blue-500 focus:outline-none focus:ring-4 focus:ring-sky-500/20 disabled:cursor-not-allowed disabled:opacity-80"
              >
                {isSubmitting ? <SpinnerLabel /> : <ArrowRight size={18} />}
                {isSubmitting ? "Signing in..." : "Sign In"}
              </button>
            </form>

            {errorMessage ? (
              <div
                role="alert"
                aria-live="polite"
                className="mt-5 flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 shadow-sm animate-[fadeIn_180ms_ease-out]"
              >
                <TriangleAlert size={18} className="mt-0.5 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            ) : null}

            <div className="mt-8 border-t border-slate-200 pt-6">
              <div className="mb-3 flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-slate-800">Demo accounts</p>
                <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">
                  No auth logic
                </span>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                {demoAccounts.map((account) => (
                  <button
                    key={account.label}
                    type="button"
                    onClick={() => handleDemoLogin(account.role)}
                    disabled={isSubmitting}
                    className="group relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm font-semibold text-slate-800 transition hover:-translate-y-0.5 hover:border-slate-300 hover:bg-white hover:shadow-md disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    <span
                      className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${account.accent}`}
                    />
                    <span className="block">{account.label}</span>
                    <span className="mt-1 block text-xs font-medium text-slate-500 transition group-hover:text-slate-600">
                      Open demo role
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function FeatureCard({ title, description, icon }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/8 p-5 backdrop-blur-sm">
      <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-cyan-100">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
    </div>
  );
}

function SpinnerLabel() {
  return <Loader2 size={18} className="animate-spin" />;
}

function getDashboardPath(role) {
  if (role === USER_ROLES.admin) {
    return ROUTE_PATHS.admin.dashboard;
  }

  if (role === USER_ROLES.assetManager) {
    return ROUTE_PATHS.manager.dashboard;
  }

  return ROUTE_PATHS.employee.dashboard;
}
