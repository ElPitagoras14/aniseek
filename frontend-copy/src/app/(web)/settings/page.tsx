import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Users from "./components/users/users";
import Storage from "./components/storage/storage";
import Season from "./components/season/season";

export default function Configuration() {
  return (
    <div className="flex flex-col gap-y-10">
      <Tabs defaultValue="season">
        <TabsList className="w-full py-5 mb-4">
          <TabsTrigger className="w-full text-base py-4" value="season">
            Season Relation
          </TabsTrigger>
          <TabsTrigger className="w-full text-base py-4" value="storage">
            Storage
          </TabsTrigger>
          <TabsTrigger className="w-full text-base py-4" value="user">
            Users
          </TabsTrigger>
        </TabsList>
        <TabsContent value="season">
          <Season />
        </TabsContent>
        <TabsContent value="storage">
          <Storage />
        </TabsContent>
        <TabsContent value="user">
          <Users />
        </TabsContent>
      </Tabs>
    </div>
  );
}
