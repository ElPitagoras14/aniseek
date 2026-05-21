import Navbar from "@/components/navbar";
import FooterNavbar from "@/components/footer-navbar";

export default function WebLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <Navbar />
      <main className="px-4 py-4 sm:px-12 sm:py-8 mb-16">{children}</main>
      <FooterNavbar />
    </>
  );
}
