import type { PropType } from 'vue';
export interface TagColor {
    color?: string;
    borderColor?: string;
    textColor?: string;
}
declare const _default: {
    readonly color: PropType<TagColor>;
    readonly type: {
        readonly type: PropType<"default" | "primary" | "success" | "info" | "warning" | "error">;
        readonly default: "default";
    };
    readonly round: BooleanConstructor;
    readonly size: {
        readonly type: PropType<"tiny" | "small" | "medium" | "large">;
        readonly default: "medium";
    };
    readonly closable: BooleanConstructor;
    readonly disabled: {
        readonly type: PropType<boolean | undefined>;
        readonly default: undefined;
    };
};
export default _default;
