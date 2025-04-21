
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { Toaster } from '@/components/ui/toaster';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow">{children}</main>
      <Footer />
      <Toaster />
    </div>
  );
}
