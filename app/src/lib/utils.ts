// Vendored from shadcn/ui (https://ui.shadcn.com) — MIT, Copyright (c) shadcn.
// Local modifications are made in place; see LICENSE.md.
// SPDX-License-Identifier: MIT
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
