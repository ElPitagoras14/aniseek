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
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getAnimesForFranchise } from "../season";
import { Item } from "@/components/autocomplete";

interface NewPrequelNodeProps {
  id: string;
}

export default function NewPrequelNode({ id }: NewPrequelNodeProps) {
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

  const outConnections = useNodeConnections({
    handleType: "source",
  });

  const newNode = {
    id: animeInfo.value,
    position: { x: currNode?.position.x || 0, y: 0 },
    data: { label: animeInfo.label },
    type: "anime",
  };

  const prequelNode = {
    id: "new-prequel",
    position: { x: (currNode?.position.x || 0) - 200, y: 0 },
    data: { label: "New Prequel" },
    type: "prequel",
  };

  const handleClick = () => {
    setNodes((prevNodes) => [prequelNode, newNode, ...prevNodes.slice(1)]);
    setEdges((prevEdges) => [
      {
        id: `new-prequel-${animeInfo.value}`,
        source: "new-prequel",
        target: animeInfo.value,
        animated: true,
      },
      ...prevEdges.map((edge) => {
        if (edge.id === outConnections[0].edgeId) {
          return {
            ...edge,
            id: `${animeInfo.value}-${edge.target}`,
            source: animeInfo.value,
          };
        }
        return edge;
      }),
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
          Add prequel
        </DialogTrigger>
        <DialogContent className="w-100">
          <DialogHeader>
            <DialogTitle>Add prequel</DialogTitle>
          </DialogHeader>
          <AutocompleteNode
            animes={animes}
            animeInfo={animeInfo}
            setAnimeInfo={setAnimeInfo}
          />
          <div className="flex justify-end">
            <Button onClick={handleClick}>Add prequel</Button>
          </div>
        </DialogContent>
      </Dialog>
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={outConnections.length === 0}
      />
    </BaseNode>
  );
}
