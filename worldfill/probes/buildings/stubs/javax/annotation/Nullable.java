package javax.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * A stub of javax.annotation.Nullable so the mod's classes compile outside a Forge build.
 *
 * Java 8 shipped this in the JDK and Java 17 does not, and the mod's own jar is not on the
 * classpath of a standalone probe (there is no gradle build here to take it from). 34 classes of
 * the mod import it, so the probe stubs it rather than editing the mod to suit the probe. It is a
 * marker only: nothing reads it at runtime, and none of these probes run reflection over it.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD, ElementType.FIELD, ElementType.PARAMETER,
         ElementType.LOCAL_VARIABLE, ElementType.TYPE_USE})
public @interface Nullable {
}
