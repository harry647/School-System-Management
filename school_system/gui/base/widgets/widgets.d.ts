/**
 * TypeScript type definitions for the School System Widget Library
 * 
 * This file provides TypeScript type definitions for all widget components
 * to enable type-safe usage in web integrations or TypeScript-based applications.
 */

declare namespace SchoolSystemWidgets {
    /**
     * Custom Table Widget
     */
    interface CustomTableWidgetOptions {
        /** Enable sorting */
        sortingEnabled?: boolean;
        /** Enable filtering */
        filteringEnabled?: boolean;
        /** Alternating row colors */
        alternatingRowColors?: boolean;
        /** Selection behavior */
        selectionBehavior?: 'SelectRows' | 'SelectColumns' | 'SelectItems';
        /** Selection mode */
        selectionMode?: 'SingleSelection' | 'MultiSelection' | 'ExtendedSelection' | 'ContiguousSelection';
    }

    interface TableDataItem {
        [key: string]: any;
    }

    class CustomTableWidget {
        constructor(parent?: any, options?: CustomTableWidgetOptions);

        /**
         * Set table data
         * @param data Array of data items
         * @param headers Array of column headers
         */
        setData(data: TableDataItem[], headers: string[]): void;

        /**
         * Sort table by column
         * @param column Column index
         * @param order Sort order ('Ascending' or 'Descending')
         */
        sortByColumn(column: number, order: 'Ascending' | 'Descending'): void;

        /**
         * Add filter widgets
         * @param filterWidgets Object mapping column names to filter widgets
         */
        addFilterWidgets(filterWidgets: {[key: string]: any}): void;

        /**
         * Apply current filters
         */
        applyFilters(): void;

        /**
         * Row selection changed signal
         */
        rowSelected: Signal<number>;
    }

    /**
     * Sort Filter Proxy Model
     */
    class SortFilterProxyModel {
        constructor(parent?: any);

        /**
         * Set filter column
         * @param column Column index to filter on
         */
        setFilterColumn(column: number): void;

        /**
         * Set filter text
         * @param text Filter text
         */
        setFilterText(text: string): void;

        /**
         * Set source model
         * @param model Source model
         */
        setSourceModel(model: any): void;
    }

    /**
     * Virtual Scroll Model
     */
    interface VirtualScrollModelOptions {
        /** Row count */
        rowCount: number;
        /** Column count */
        columnCount: number;
        /** Headers */
        headers: string[];
        /** Data provider function */
        dataProvider: (row: number, col: number) => any;
    }

    class VirtualScrollModel {
        constructor(options: VirtualScrollModelOptions, parent?: any);

        /**
         * Get row count
         */
        rowCount(): number;

        /**
         * Get column count
         */
        columnCount(): number;

        /**
         * Get data for index
         */
        data(index: any, role: number): any;
    }

    /**
     * Search Box Widget
     */
    interface SearchBoxOptions {
        /** Placeholder text */
        placeholderText?: string;
        /** Debounce delay in milliseconds */
        debounceDelay?: number;
    }

    class SearchBox {
        constructor(options?: SearchBoxOptions, parent?: any);

        /**
         * Get current search text
         */
        getSearchText(): string;

        /**
         * Set search text
         * @param text Search text
         */
        setSearchText(text: string): void;

        /**
         * Clear search input
         */
        clear(): void;

        /**
         * Set debounce delay
         * @param delayMs Delay in milliseconds
         */
        setDebounceDelay(delayMs: number): void;

        /**
         * Set placeholder text
         * @param text Placeholder text
         */
        setPlaceholderText(text: string): void;

        /**
         * Search text changed signal
         */
        searchTextChanged: Signal<string>;
    }

    /**
     * Advanced Search Box
     */
    class AdvancedSearchBox extends SearchBox {
        constructor(options?: SearchBoxOptions, parent?: any);
        // Inherits all SearchBox methods and properties
    }

    /**
     * Memoized Search Box
     */
    interface MemoizedSearchBoxOptions extends SearchBoxOptions {
        /** Cache size */
        cacheSize?: number;
    }

    class MemoizedSearchBox extends SearchBox {
        constructor(options?: MemoizedSearchBoxOptions, parent?: any);

        /**
         * Set cache size
         * @param size Maximum cache size
         */
        setCacheSize(size: number): void;

        /**
         * Clear cache
         */
        clearCache(): void;
    }

    /**
     * Modern Status Bar
     */
    class ModernStatusBar {
        constructor(parent?: any);

        /**
         * Show progress
         * @param value Current progress value
         * @param maxValue Maximum progress value
         */
        showProgress(value: number, maxValue?: number): void;

        /**
         * Hide progress bar
         */
        hideProgress(): void;

        /**
         * Show message
         * @param message Message text
         * @param timeout Duration in milliseconds (0 for permanent)
         */
        showMessage(message: string, timeout?: number): void;

        /**
         * Clear current message
         */
        clearMessage(): void;

        /**
         * Show temporary message
         * @param message Message text
         * @param duration Duration in milliseconds
         */
        showTemporaryMessage(message: string, duration?: number): void;

        /**
         * Show permanent message
         * @param message Message text
         */
        showPermanentMessage(message: string): void;
    }

    /**
     * Progress Indicator
     */
    interface ProgressIndicatorOptions {
        /** Size in pixels */
        size?: number;
        /** Current value */
        value?: number;
        /** Maximum value */
        maxValue?: number;
        /** Color */
        color?: string;
    }

    class ProgressIndicator {
        constructor(options?: ProgressIndicatorOptions, parent?: any);

        /**
         * Set current value
         * @param value Current progress value
         */
        setValue(value: number): void;

        /**
         * Set maximum value
         * @param maxValue Maximum progress value
         */
        setMaxValue(maxValue: number): void;

        /**
         * Set color
         * @param color Color string
         */
        setColor(color: string): void;
    }

    /**
     * Signal type for widget events
     */
    interface Signal<T> {
        /**
         * Connect a callback to the signal
         * @param callback Callback function
         */
        connect(callback: (value: T) => void): void;

        /**
         * Disconnect a callback from the signal
         * @param callback Callback function
         */
        disconnect(callback: (value: T) => void): void;

        /**
         * Emit the signal
         * @param value Value to emit
         */
        emit(value: T): void;
    }

    /**
     * Theme Manager
     */
    interface ThemeColors {
        primary: string;
        secondary: string;
        background: string;
        text: string;
        border: string;
    }

    interface ThemeManager {
        /**
         * Set current theme
         * @param themeName Theme name
         */
        setTheme(themeName: string): void;

        /**
         * Get current theme
         */
        getTheme(): string;

        /**
         * Get color from current theme
         * @param colorName Color name
         */
        getColor(colorName: string): string;

        /**
         * Add custom theme
         * @param themeName Theme name
         * @param themeDict Theme color dictionary
         */
        addTheme(themeName: string, themeDict: ThemeColors): void;

        /**
         * Generate QSS for current theme
         */
        generateQSS(): string;

        /**
         * Theme changed signal
         */
        themeChanged: Signal<string>;
    }
}

declare module 'school-system-widgets' {
    export = SchoolSystemWidgets;
}