import { BaseNode, BaseNodeContent } from "@/components/base-node";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Handle,
  Position,
  useNodeConnections,
  useReactFlow,
} from "@xyflow/react";
import { useState } from "react";

interface AnimeNodeProps {
  id: string;
  data: {
    label: string;
    season: number;
  };
}

export function AnimeNode({ id, data }: AnimeNodeProps) {
  const [season, setSeason] = useState<number>(data.season || 1);

  const { setNodes } = useReactFlow();

  const inConnections = useNodeConnections({
    handleType: "source",
  });
  const outConnections = useNodeConnections({
    handleType: "target",
  });

  const updateNodeSeason = (value: string) => {
    const season = parseInt(value);
    setSeason(season);
    setNodes((prevNodes) => {
      return prevNodes.map((node) => {
        if (node.id === id) {
          return {
            ...node,
            data: {
              ...node.data,
              season,
            },
          };
        }
        return node;
      });
    });
  };

  return (
    <BaseNode className="bg-muted">
      <BaseNodeContent>
        <p className="text-sm">{data.label}</p>
        <div className="flex flex-row text-sm text-muted-foreground gap-x-2">
          <Label>Season</Label>
          <Input
            value={season}
            onChange={(e) => {
              updateNodeSeason(e.target.value);
            }}
            placeholder="Season..."
            type="number"
            className="nodrag w-14 text-xs h-8"
          />
        </div>
      </BaseNodeContent>
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={outConnections.length === 0}
      />
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={inConnections.length === 0}
      />
    </BaseNode>
  );
}
