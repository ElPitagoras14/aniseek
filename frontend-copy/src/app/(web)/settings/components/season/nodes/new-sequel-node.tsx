import { BaseNode } from "@/components/base-node";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Handle,
  Position,
  useNodeConnections,
  useReactFlow,
} from "@xyflow/react";
import AutocompleteNode from "./autocomplete-node";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { getAnimesForFranchise } from "../season";
import { Item } from "@/components/autocomplete";

interface NewSequelNodeProps {
  id: string;
}

export default function NewSequelNode({ id }: NewSequelNodeProps) {
  const [open, setOpen] = useState<boolean>(false);
  const [animeInfo, setAnimeInfo] = useState<Item>({
    value: "",
    label: "",
  });

  const { setNodes, getNode, setEdges } = useReactFlow();

  const { data } = useQuery({
    queryKey: ["animes"],
    queryFn: getAnimesForFranchise,
    refetchOnWindowFocus: false,
  });

  const animes = data?.data?.payload?.items || [];

  const currNode = getNode(id);

  const inConnections = useNodeConnections({
    handleType: "target",
  });

  const newNode = {
    id: animeInfo.value,
    position: { x: currNode?.position.x || 0, y: 0 },
    data: { label: animeInfo.label },
    type: "anime",
  };

  const sequelNode = {
    id: "new-sequel",
    position: { x: (currNode?.position.x || 0) + 200, y: 0 },
    data: { label: "New Sequel" },
    type: "sequel",
  };

  const handleClick = () => {
    setNodes((prevNodes) => [...prevNodes.slice(0, -1), newNode, sequelNode]);
    setEdges((prevEdges) => [
      ...prevEdges.map((edge) => {
        if (edge.id === inConnections[0].edgeId) {
          return {
            ...edge,
            id: `${edge.source}-${animeInfo.value}`,
            target: animeInfo.value,
          };
        }
        return edge;
      }),
      {
        id: `${animeInfo.value}-new-sequel`,
        source: animeInfo.value,
        target: "new-sequel",
        animated: true,
      },
    ]);
    setAnimeInfo({
      value: "",
      label: "",
    });
    setOpen(false);
  };

  return (
    <BaseNode className="text-sm">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger className="text-xs m-4 p-1 nodrag cursor-pointer">
          Add sequel
        </DialogTrigger>
        <DialogContent className="w-100">
          <DialogHeader>
            <DialogTitle>Add sequel</DialogTitle>
          </DialogHeader>
          <AutocompleteNode
            animes={animes}
            animeInfo={animeInfo}
            setAnimeInfo={setAnimeInfo}
          />
          <div className="flex justify-end">
            <Button onClick={handleClick}>Add sequel</Button>
          </div>
        </DialogContent>
      </Dialog>
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={inConnections.length === 0}
      />
    </BaseNode>
  );
}
