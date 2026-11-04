package org.slf4j; public interface Logger { default void info(String s,Object... v){} default void warn(String s,Object... v){} }
