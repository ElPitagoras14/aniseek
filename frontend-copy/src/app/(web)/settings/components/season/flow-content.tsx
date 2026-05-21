"use client";

import { useCallback, useState } from "react";
import {
  ReactFlow,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  getIncomers,
  getOutgoers,
  getConnectedEdges,
  Edge,
  Node,
  OnConnect,
  OnDelete,
  ReactFlowProvider,
  Controls,
  Panel,
  OnNodesChange,
  applyNodeChanges,
  OnEdgesDelete,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useTheme } from "next-themes";
import { Input } from "@/components/ui/input";
import { AnimeNode } from "./nodes/anime-node";
import NewSequelNode from "./nodes/new-sequel-node";
import NewPrequelNode from "./nodes/new-prequel-node";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import apiClient from "@/lib/api-client";
import { toast } from "sonner";
import { ArrowLeftIcon } from "lucide-react";
import { AxiosError } from "axios";

const nodeTypes = {
  anime: AnimeNode,
  sequel: NewSequelNode,
  prequel: NewPrequelNode,
};

const protectedNodes = ["new-prequel", "new-sequel"];

interface FranchiseInfo {
  franchise: string;
  animes: {
    id: string;
    season: number;
  }[];
}

const createFranchise = async (franchiseInfo: FranchiseInfo) => {
  const options = {
    method: "POST",
    url: "/franchises",
    data: franchiseInfo,
  };

  return apiClient(options);
};

interface FlowContentProps {
  baseId: string;
  baseTitle: string;
  setMode: (mode: "select" | "create") => void;
}

export default function FlowContent({
  baseId,
  baseTitle,
  setMode,
}: FlowContentProps) {
  const initialNodes: Node[] = [
    {
      id: "new-prequel",
      position: { x: -200, y: 0 },
      data: {},
      type: "prequel",
    },
    {
      id: baseId,
      position: { x: 0, y: 0 },
      data: { label: baseTitle, season: 1 },
      type: "anime",
    },
    {
      id: "new-sequel",
      position: { x: 200, y: 0 },
      data: {},
      type: "sequel",
    },
  ];

  const initialEdges: Edge[] = [
    {
      id: `new-prequel-${baseId}`,
      source: "new-prequel",
      target: baseId,
      animated: true,
    },
    {
      id: `${baseId}-new-sequel`,
      source: baseId,
      target: "new-sequel",
      animated: true,
    },
  ];

  const [nodes, setNodes] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const [franchise, setFranchise] = useState<string>("");

  const { theme } = useTheme();

  const handleCreateFranchise = useMutation({
    mutationFn: createFranchise,
    onSuccess: () => {
      toast.success("Franchise created successfully");
      console.log("Successfully created franchise");
    },
    onError: (err) => {
      console.log("Error creating franchise");
      if (err && err instanceof AxiosError && err.response) {
        toast.error(err.response.data.message);
        return;
      }
      toast.error("Error creating franchise");
    },
  });

  const onConnect: OnConnect = useCallback(
    (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      setNodes((currentNodes) => {
        const filteredChanges = changes.filter((change) => {
          if (change.type === "remove" && protectedNodes.includes(change.id)) {
            return false;
          }
          return true;
        });

        return applyNodeChanges(filteredChanges, currentNodes);
      });
    },
    [setNodes]
  );

  const onNodesDelete: OnDelete = useCallback(
    (deleted) => {
      let remainingNodes = [...nodes];

      setEdges(
        deleted.nodes.reduce((acc, node: Node) => {
          if (protectedNodes.includes(node.id)) return acc;

          const incomers = getIncomers(node, remainingNodes, acc);
          const outgoers = getOutgoers(node, remainingNodes, acc);
          const connectedEdges = getConnectedEdges([node], acc);

          const remainingEdges = acc.filter(
            (edge: Edge) => !connectedEdges.includes(edge)
          );

          const createdEdges = incomers.flatMap(({ id: source }) =>
            outgoers.map(({ id: target }) => ({
              id: `${source}->${target}`,
              source,
              target,
              animated: true,
            }))
          );

          remainingNodes = remainingNodes.filter((rn) => rn.id !== node.id);

          return [...remainingEdges, ...createdEdges];
        }, edges)
      );
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [nodes, edges]
  );

  const onEdgesDelete: OnEdgesDelete = useCallback(() => {
    setEdges((prev) => [...prev]);
  }, [setEdges]);

  const handleCreateSeason = () => {
    const animeNodes = nodes.slice(1, -1).map((node) => ({
      id: node.id,
      season: node.data.season as number,
    }));
    const franchiseInfo = {
      franchise: franchise,
      animes: animeNodes,
    };

    handleCreateFranchise.mutate(franchiseInfo);
  };

  const canUpdate = franchise !== "" && nodes.length > 2;
  const checkAscendingNodes = () => {
    if (nodes.length < 3) return false;
    const seasons: number[] = nodes
      .slice(1, nodes.length - 1)
      .map((node) => node.data.season as number);
    return seasons
      .slice(0, -1)
      .every((season, idx) => season < seasons[idx + 1]);
  };

  return (
    <div className="w-full h-[74svh]">
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onDelete={onNodesDelete}
          onConnect={onConnect}
          onEdgesChange={onEdgesChange}
          onEdgesDelete={onEdgesDelete}
          nodeTypes={nodeTypes}
          colorMode={theme === "light" ? "light" : "dark"}
          fitView
          className="rounded-md"
        >
          <Background />
          <Controls />
          <Panel position="top-left">
            <Button
              variant="ghost"
              size="icon"
              className="cursor-pointer"
              onClick={() => setMode("select")}
            >
              <ArrowLeftIcon />
            </Button>
          </Panel>
          <Panel position="top-center">
            <Input
              placeholder="Franchise"
              value={franchise}
              onChange={(e) => setFranchise(e.target.value)}
            />
          </Panel>
          <Panel position="top-right">
            <div className="flex flex-col gap-y-4 items-end">
              <Button
                disabled={!canUpdate}
                onClick={handleCreateSeason}
                className="cursor-pointer"
              >
                Create Season
              </Button>
              <div className="flex flex-col text-end gap-y-0">
                {!franchise && (
                  <p className="text-red-500">Fill a franchise name</p>
                )}
                {nodes.length < 3 && (
                  <p className="text-red-500">
                    Franchise must have at least 1 anime
                  </p>
                )}
                {!checkAscendingNodes() && (
                  <p className="text-red-500">
                    Franchise must have seasons in ascending order
                  </p>
                )}
              </div>
            </div>
          </Panel>
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
