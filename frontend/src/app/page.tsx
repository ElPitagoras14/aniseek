import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Download, 
  Search, 
  Bookmark, 
  FolderKanban,
  CalendarDays,
  HardDrive,
  Clapperboard,
  Users
} from "lucide-react";
import Link from "next/link";
import LandingNavbar from "@/components/landing-navbar";

const features = [
  {
    icon: Search,
    title: "Search",
    description: "Find any anime from multiple sources with a powerful search engine."
  },
  {
    icon: Bookmark,
    title: "Save",
    description: "Keep track of your favorite animes in your personal library."
  },
  {
    icon: Download,
    title: "Download",
    description: "Download episodes individually or in bulk to watch offline."
  },
  {
    icon: CalendarDays,
    title: "Follow",
    description: "Track ongoing series and never miss a new episode release."
  }
];

const benefits = [
  {
    icon: Users,
    title: "Multi-User",
    description: "Share the instance with friends and family. Each user has their own library."
  },
  {
    icon: FolderKanban,
    title: "Franchises",
    description: "Organize related anime series into franchises to keep everything tidy."
  },
  {
    icon: HardDrive,
    title: "Local Storage",
    description: "All your downloads are stored locally on your own storage."
  }
];

export default async function Page() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNavbar />

      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center py-16 sm:py-20 lg:py-24 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="flex flex-col items-center text-center gap-8">
            <Badge variant="secondary" className="px-4 py-1.5 text-sm">
              Your anime, your way
            </Badge>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
              Build Your Own{" "}
              <span className="text-primary">Anime Library</span>
            </h1>
            
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl">
              Search, save, and download anime to create your personal library. 
              Watch offline, organize your collection, and follow your favorite series.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 mt-6">
              <Button asChild size="lg" className="text-base px-8">
                <Link href="/register">
                  Get Started
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="text-base px-8">
                <Link href="/login">
                  Sign In
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-muted/30">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center gap-4 mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              What You Can Do
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl">
              Everything you need to manage your anime collection
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {features.map((feature, index) => (
              <Card key={index} className="border-2 hover:border-primary/30 transition-colors">
                <CardHeader className="pb-4">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 sm:py-20 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center gap-4 mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Why Use Aniseek
            </h2>
            <p className="text-muted-foreground text-lg max-w-xl">
              A simple tool for anime fans
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {benefits.map((benefit, index) => (
              <Card key={index} className="text-center p-6">
                <CardHeader className="pb-4">
                  <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-3">
                    <benefit.icon className="w-7 h-7 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {benefit.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center text-center gap-6">
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Start Building Your Library
            </h2>
            <p className="text-primary-foreground/80 text-lg max-w-lg">
              Create an account and start saving and downloading your favorite anime today.
            </p>
            <Button 
              asChild 
              size="lg" 
              variant="secondary" 
              className="text-base px-10 mt-4"
            >
              <Link href="/register">
                Create Account
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 border-t">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Clapperboard className="w-5 h-5" />
              <span className="font-semibold">Aniseek</span>
            </div>
            <p className="text-muted-foreground text-sm">
              Built for anime fans
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
