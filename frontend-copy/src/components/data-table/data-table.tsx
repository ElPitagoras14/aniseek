"use client";

import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  PaginationState,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { DataTablePagination } from "./pagination";
import { cn } from "@/lib/utils";
import { SetStateAction, useState } from "react";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  serverSide?: {
    pagination?: {
      value: PaginationState;
      onChange: (pagination: SetStateAction<PaginationState>) => void;
    };
    sorting?: {
      value: SortingState;
      setValue: (sorting: SetStateAction<SortingState>) => void;
    };
    columnFilters?: {
      value: ColumnFiltersState;
      setValue: (columnFilters: SetStateAction<ColumnFiltersState>) => void;
    };
    totalRows: number;
    isLoading: boolean;
  };
  enableSelect?: boolean;
  tableClassName?: string;
  containerClassName?: string;
}

export function DataTable<TData, TValue>({
  columns,
  data,
  serverSide,
  enableSelect = true,
  tableClassName,
  containerClassName,
}: DataTableProps<TData, TValue>) {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: serverSide?.pagination ? true : false,
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: serverSide?.pagination?.onChange || setPagination,
    manualSorting: serverSide?.sorting ? true : false,
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: serverSide?.sorting?.setValue || setSorting,
    manualFiltering: serverSide?.columnFilters ? true : false,
    getFilteredRowModel: getFilteredRowModel(),
    onColumnFiltersChange:
      serverSide?.columnFilters?.setValue || setColumnFilters,
    rowCount: serverSide?.totalRows || data.length,
    state: {
      sorting: serverSide?.sorting?.value || sorting,
      pagination: serverSide?.pagination?.value || pagination,
      columnFilters: serverSide?.columnFilters?.value || columnFilters,
    },
  });

  return (
    <div className={cn("flex flex-col gap-y-4", containerClassName)}>
      <div className={cn("overflow-hidden rounded-md border", tableClassName)}>
        <Table>
          <TableHeader className="border-b">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-b">
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <DataTablePagination table={table} enableSelect={enableSelect} />
    </div>
  );
}
