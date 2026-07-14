import { db } from "@/db";
import { sql } from "drizzle-orm";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  await db.execute(sql`select 1`);

  return (
    <main className="grid min-h-screen place-items-center px-6 py-12">
      <section className="w-full max-w-2xl rounded-3xl bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700/50 p-10 shadow-[0_24px_60px_rgba(0,0,0,0.4)]">
        <div className="text-center">
          <p className="text-5xl mb-4">🌿</p>
          <h1 className="text-5xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent tracking-tight">
            Luvén
          </h1>
          <p className="mt-2 text-sm uppercase tracking-[0.2em] text-slate-500 font-semibold">
            Kişisel Diyet & Kalori Takip
          </p>
          <div className="mt-8 space-y-4 text-left">
            <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/30">
              <h3 className="text-lg font-bold text-indigo-400 mb-2">🤖 Gemini AI Destekli</h3>
              <p className="text-slate-400 text-sm">Yapay zeka ile kişiselleştirilmiş diyet programları ve kalori hesaplama</p>
            </div>
            <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/30">
              <h3 className="text-lg font-bold text-purple-400 mb-2">📊 Vücut Takibi</h3>
              <p className="text-slate-400 text-sm">Kilo, yağ oranı, kas oranı ve su yüzdesi takibi — günlük ve aylık gelişim analizi</p>
            </div>
            <div className="bg-slate-800/50 rounded-2xl p-5 border border-slate-700/30">
              <h3 className="text-lg font-bold text-sky-400 mb-2">🍽️ Kalori Takibi</h3>
              <p className="text-slate-400 text-sm">Yemek girişi ile otomatik kalori ve makro hesaplama</p>
            </div>
          </div>
          <div className="mt-8 p-4 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
            <p className="text-indigo-300 text-sm">
              Bu uygulama Streamlit ile çalışmaktadır.<br />
              <code className="bg-slate-800 px-2 py-1 rounded text-xs mt-1 inline-block">streamlit run app.py</code>
            </p>
          </div>
          <p className="mt-6 text-xs text-slate-600">
            Powered by Gemini AI — Kişisel kullanım için tasarlandı
          </p>
        </div>
      </section>
    </main>
  );
}
